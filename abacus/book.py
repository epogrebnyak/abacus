from dataclasses import field
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from abacus.accounting_types import (
    AbacusError,
    AccountBalancesDict,
    AccountName,
    Amount,
    Entry,
    MultipleEntry,
)
from abacus.chart import Chart
from abacus.closing import (
    CloseContraExpense,
    CloseContraIncome,
    CloseExpense,
    CloseIncome,
    CloseISA,
    closing_entries,
)
from abacus.closing_types import ClosingEntry
from abacus.ledger import Ledger, process_postings


def yield_until(xs, classes):
    for x in xs:
        if any(isinstance(x, cls) for cls in classes):
            break
        yield x


def to_multiple_entry(ledger, starting_balances: dict) -> MultipleEntry:
    me = MultipleEntry([], [])
    for account_name, amount in starting_balances.items():
        account = ledger[account_name]
        t = (account_name, amount)
        if account.is_debit_account():
            me.debit_entries.append(t)
        if account.is_credit_account():
            me.credit_entries.append(t)
    return me


def choose_entries_for_closing_temp_contra_accounts(
    closing_entries: List[ClosingEntry],
):
    """Return close contra income and close contra expense accounts.
    Used to construct income statement."""
    return [
        p
        for p in closing_entries
        if isinstance(p, CloseContraExpense)
        or isinstance(p, CloseContraIncome)
        or p.action in ["close_contra_expense", "close_contra_income"]
    ]


@dataclass
class Entries:
    business: List[Entry] = field(default_factory=list)
    adjustment: List[Entry] = field(default_factory=list)
    closing: List[
        CloseContraIncome | CloseContraExpense | CloseIncome | CloseExpense | CloseISA
    ] = field(default_factory=list)
    post_close: List[Entry] = field(default_factory=list)

    def yield_for_income_statement(self):
        entry_lists = [
            self.business,
            self.adjustment,
            choose_entries_for_closing_temp_contra_accounts(self.closing),
            self.post_close,
        ]
        for entry_list in entry_lists:
            for entry in entry_list:
                yield entry

    def yield_all(self):
        entry_lists = [
            self.business,
            self.adjustment,
            self.closing,
            self.post_close,
        ]
        for entry_list in entry_lists:
            for entry in entry_list:
                yield entry


class Book(BaseModel):
    chart: Chart = Chart.empty()
    starting_balances: Dict[AccountName, Amount] = {}
    entries: Entries = Entries()

    @property
    def is_closed(self) -> bool:
        return len(self.entries.closing) > 0

    def save(self, path: str):
        Path(path).write_text(self.json(indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str):
        return cls.parse_file(path)

    def assert_book_was_not_closed(self):
        if self.is_closed:
            raise AbacusError("Cannot add entries to closed ledger.")

    def post_many(self, entries: List[Entry]) -> "Book":
        self.entries.business.extend(entries)
        return self

    def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Book":
        entry = Entry(dr, cr, amount)
        self.entries.business.append(entry)
        return self

    def adjust(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Book":
        entry = Entry(dr, cr, amount)
        self.entries.adjustment.append(entry)
        return self

    def post_close(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Book":
        entry = Entry(dr, cr, amount)
        self.entries.post_close.append(entry)
        return self

    def close(self):
        if self.is_closed:
            raise AbacusError("Ledger already closed, cannot close again.")
        self.entries.closing = closing_entries(self.ledger(), self.chart.contra_accounts)  # type: ignore
        return self

    def ledger(self):
        return ledger_all(self)

    def balances(self) -> AccountBalancesDict:
        return self.ledger().balances()

    def nonzero_balances(self) -> AccountBalancesDict:
        return AccountBalancesDict({k: v for k, v in self.balances().items() if v != 0})

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self.ledger(), self.chart.contra_accounts)

    def income_statement(self):
        from .reports import income_statement

        return income_statement(ledger_for_income_statement(self))


def empty_ledger(book: Book) -> Ledger:
    """Return blank ledger with account structure from `book.chart`."""
    return book.chart.ledger()


def starting_entry(book: Book):
    return to_multiple_entry(empty_ledger(book), book.starting_balances)


def ledger_with_starting_balances(book: Book) -> Ledger:
    """Ledger with starting balances."""
    me = starting_entry(book)
    return empty_ledger(book).process_postings([me])


def ledger_all(book: Book) -> Ledger:
    """Return final ledger after processing all entries."""
    _ledger = ledger_with_starting_balances(book)
    postings = book.entries.yield_all()
    return process_postings(_ledger, postings)


def ledger_for_income_statement(book: Book) -> Ledger:
    """Return ledger for creating income statement.
    This ledger excludes closing entries that remove
    income and expenses information, but includes post-close entries."""
    _ledger = ledger_with_starting_balances(book)
    postings = book.entries.yield_for_income_statement()
    return process_postings(_ledger, postings)


# class BaseJournal(BaseModel):
#     chart: Chart
#     starting_balances: dict = {}
#     business_entries: list[Entry] = []
#     adjustment_entries: list[Entry] = []
#     closing_entries: list[ClosingEntry] = []
#     post_close_entries: list[Entry] = []
#     is_closed: bool = False

#     @property
#     def netting(self) -> Netting:
#         return self.chart.contra_accounts

#     def starting_entry(self) -> MultipleEntry:
#         return to_multiple_entry(self.empty_ledger, self.starting_balances)

#     def entries_for_closing_temp_contra_accounts(self):
#         """Return close contra income and close contra expense accounts.
#         Used to construct income statement."""
#         from abacus.closing_types import CloseContraExpense, CloseContraIncome

#         return [
#             p
#             for p in self.closing_entries
#             if isinstance(p, CloseContraExpense)
#             or isinstance(p, CloseContraIncome)
#             or p.action in ["close_contra_expense", "close_contra_income"]
#         ]

#     def yield_for_income_statement(self):
#         entry_lists = [
#             self.business_entries,
#             self.adjustment_entries,
#             self.entries_for_closing_temp_contra_accounts(),
#             self.post_close_entries,
#         ]
#         for entry_list in entry_lists:
#             for entry in entry_list:
#                 yield entry

#     def yield_all(self):
#         entry_lists = [
#             self.business_entries,
#             self.adjustment_entries,
#             self.closing_entries,
#             self.post_close_entries,
#         ]
#         for entry_list in entry_lists:
#             for entry in entry_list:
#                 yield entry

#     @property
#     def empty_ledger(self):
#         return self.chart.ledger()

#     @property
#     def start_ledger(self):
#         """Ledger with some balances."""
#         return self.empty_ledger.process_postings([self.starting_entry()])

#     def process(self, postings):
#         return process_postings(self.start_ledger, postings)

#     def ledger(self):
#         return self.process(self.yield_all())

#     def ledger_for_income_statement(self):
#         _gen = self.yield_for_income_statement()
#         return self.process(_gen)

#     def add_business_entries(self, ps: list[Entry]):
#         if self.is_closed:
#             raise AbacusError("Cannot add entries to closed ledger.")
#         self.business_entries.extend(ps)
#         return self

#     def add_adjustment_entries(self, ps: list[Entry]):
#         if self.is_closed:
#             raise AbacusError("Cannot add entries to closed ledger.")
#         self.business_entries.extend(ps)
#         return self

#     def close(self):
#         from abacus.closing import closing_entries

#         if self.is_closed:
#             raise AbacusError("Ledger already closed, cannot close again.")
#         self.closing_entries = closing_entries(self.ledger(), self.netting)  # type: ignore
#         self.is_closed = True
#         return self

#     def add_post_close_entries(self, ps: list[Entry]):
#         self.post_close_entries.extend(ps)
#         return self


# class Journal(BaseModel):
#     data: BaseJournal

#     def save(self, path: str):
#         from pathlib import Path

#         Path(path).write_text(self.data.json(indent=2), encoding="utf-8")

#     @classmethod
#     def load(cls, path: str):
#         return Journal(data=BaseJournal.parse_file(path))

#     def post_many(self, entries: List[Entry]) -> "Journal":
#         self.data.business_entries.extend(entries)
#         return self

#     def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
#         entry = BusinessEntry(dr, cr, amount)
#         return self.post_many([entry])

#     def adjust(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
#         raise NotImplementedError

#     def post_close(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
#         raise NotImplementedError

#     def close(self) -> "Journal":
#         self.data.close()
#         return self

#     def ledger(self):
#         return self.data.ledger()

#     def balances(self) -> AccountBalancesDict:
#         return self.ledger().balances()

#     def nonzero_balances(self):
#         return AccountBalancesDict({k: v for k, v in self.balances().items() if v != 0})

#     def balance_sheet(self):
#         from .reports import balance_sheet

#         return balance_sheet(self.data.ledger(), self.data.netting)

#     def income_statement(self):
#         from .reports import income_statement

#         return income_statement(self.data.ledger_for_income_statement())

#     def current_profit(self) -> Amount:
#         return self.income_statement().current_profit()
