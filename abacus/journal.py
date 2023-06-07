from typing import List

from pydantic import BaseModel

from abacus.accounting_types import (
    AbacusError,
    AccountName,
    Amount,
    BusinessEntry,
    Entry,
)
from abacus.accounts import OpenAccount
from abacus.closing_types import ClosingEntry
from abacus.ledger import (
    Ledger,
    process_postings,
)


def yield_until(xs, classes):
    for x in xs:
        if any(isinstance(x, cls) for cls in classes):
            break
        yield x


def isin(x, classes):
    return any(isinstance(x, cls) for cls in classes)


class BaseJournal(BaseModel):
    open_accounts: list[OpenAccount] = []
    business_entries: list[Entry] = []
    adjustment_entries: list[Entry] = []
    closing_entries: list[ClosingEntry] = []
    post_close_entries: list[Entry] = []
    is_closed: bool = False

    def entries_for_closing_temp_contra_accounts(self):
        """Return close contra income and close contra expense accounts.
        Used to construct income statement."""
        from abacus.closing_types import CloseContraExpense, CloseContraIncome

        return [
            p
            for p in self.closing_entries
            if isin(p, [CloseContraExpense, CloseContraIncome])
        ]

    def yield_for_income_statement(self):
        entry_lists = [
            self.business_entries,
            self.adjustment_entries,
            self.entries_for_closing_temp_contra_accounts(),
            self.post_close_entries,
        ]
        for entry_list in entry_lists:
            for entry in entry_list:
                yield entry

    def yield_all(self):
        entry_lists = [
            self.business_entries,
            self.adjustment_entries,
            self.closing_entries,
            self.post_close_entries,
        ]
        for entry_list in entry_lists:
            for entry in entry_list:
                yield entry

    @property
    def start_ledger(self):
        return Ledger.from_stream(self.open_accounts)

    def process(self, postings):
        return process_postings(self.start_ledger, postings)

    def ledger(self):
        return self.process(self.yield_all())

    def ledger_for_income_statement(self):
        _gen = self.data.yield_for_income_statement()
        return self.data.process(_gen)

    def add_business_entries(self, ps: list[Entry]):
        if self.is_closed:
            raise AbacusError("Cannot add entries to closed ledger.")
        self.business_entries.extend(ps)
        return self

    def add_adjustment_entries(self, ps: list[Entry]):
        if self.is_closed:
            raise AbacusError("Cannot add entries to closed ledger.")
        self.business_entries.extend(ps)
        return self

    def close(self):
        from abacus.closing import closing_entries

        if self.is_closed:
            raise AbacusError("Ledger already closed.")
        self.closing_entries = closing_entries(self.ledger())  # type: ignore
        self.is_closed = True
        return self

    def add_post_close_entries(self, ps: list[Entry]):
        self.post_close_entries.extend(ps)
        return self


class Journal(BaseModel):
    data: BaseJournal = BaseJournal()

    @classmethod
    def from_file(cls, path) -> "Journal":
        raise NotImplementedError

    def save(self, path: str):
        from pathlib import Path

        Path(path).write_text(self.json(indent=2), encoding="utf-8")

    #def start(self, starting_balances):
    #    for name, amount in starting_balances.items:    
    

    def post_many(self, entries: List[Entry]) -> "Journal":
        self.data.business_entries.extend(entries)
        return self

    def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
        entry = BusinessEntry(dr, cr, amount)
        return self.post_many([entry])

    def adjust(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
        raise NotImplementedError

    def post_close(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
        raise NotImplementedError

    def close(self) -> "Journal":
        self.data.close()
        return self

    def ledger(self):
        return self.data.ledger()

    def balances(self):
        from .reports import balances

        return balances(self.ledger())

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self.data.ledger())

    def income_statement(self):
        from .reports import income_statement

        return income_statement(self.data.ledger_for_income_statement())

    def current_profit(self) -> Amount:
        return self.income_statement().current_profit()


# class Journal(UserList[Posting]):
#     """A list of postings."""

#     # def is_closed(self) -> bool:
#     #     # - income and expense contra accounts are zero
#     #     # - income and expense accounts are zero
#     #     # - isa is zero
#     #     raise NotImplementedError


#     def post_many(self, entries: List[Posting]) -> "Journal":
#         self.data.extend(entries)
#         return self

#     def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
#         entry = BusinessEntry(dr, cr, amount)
#         return self.post_many([entry])

#     def adjust(self, dr, cr, amount) -> "Journal":
#         raise NotImplementedError

#     def post_close(self, dr, cr, amount) -> "Journal":
#         raise NotImplementedError

#     def close(self) -> "Journal":
#         from abacus.closing import closing_entries

#         self.post_many(closing_entries(self.ledger()))  # type: ignore
#         return self

#     def current_profit(self):
#         return self.income_statement().current_profit()

#     def ledger(self):
#         return process_postings(Ledger(), self.data)

#     def balances(self):
#         from .reports import balances

#         return balances(self.ledger())

#     def balance_sheet(self):
#         from .reports import balance_sheet

#         return balance_sheet(self.ledger())

#     def income_statement(self):
#         from .reports import income_statement

#         _gen = yield_until(self.data, [CloseExpense, CloseIncome])
#         _ledger = process_postings(Ledger(), _gen)
#         return income_statement(_ledger)
