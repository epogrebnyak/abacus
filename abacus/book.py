from dataclasses import field
from itertools import chain
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
from abacus.chart import QualifiedChart
from abacus.closing import ClosingEntries, make_closing_entries
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


@dataclass
class Entries:
    business: List[Entry] = field(default_factory=list)
    adjustment: List[Entry] = field(default_factory=list)
    closing: ClosingEntries = ClosingEntries()
    after_close: List[Entry] = field(default_factory=list)

    def yield_for_income_statement(self):
        return chain(
            self.business,
            self.adjustment,
            self.closing.contra_expense_contra_income(),
            self.after_close,
        )

    def yield_all(self):
        return chain(
            self.business,
            self.adjustment,
            self.closing.all(),
            self.after_close,
        )


class Book(BaseModel):
    chart: QualifiedChart = QualifiedChart.empty()
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

    def post(self, debit: AccountName, credit: AccountName, amount: Amount) -> "Book":
        entry = Entry(debit, credit, amount)
        self.entries.business.append(entry)
        return self

    def post_operation(self, operation_name: str, amount: Amount):
        op = self.chart.get_operation(operation_name)
        if not op:
            raise AbacusError(op)
        return self.post(op.debit, op.credit, amount)

    def adjust(self, debit: AccountName, credit: AccountName, amount: Amount) -> "Book":
        entry = Entry(debit, credit, amount)
        self.entries.adjustment.append(entry)
        return self

    def after_close(
        self, debit: AccountName, credit: AccountName, amount: Amount
    ) -> "Book":
        entry = Entry(debit, credit, amount)
        self.entries.after_close.append(entry)
        return self

    def close(self):
        if self.is_closed:
            raise AbacusError("Ledger already closed, cannot close again.")
        self.entries.closing = make_closing_entries(
            self.ledger(), self.chart.contra_accounts
        )  # type: ignore
        return self

    def ledger(self):
        return ledger_all(self)

    def balances(self) -> AccountBalancesDict:
        return self.ledger().balances()

    def nonzero_balances(self) -> AccountBalancesDict:
        d: AccountBalancesDict = {k: v for k, v in self.balances().items() if v != 0}
        return d

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
