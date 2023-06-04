from collections import UserList
from typing import List

from pydantic import BaseModel

from abacus.accounting_types import (
    AccountName,
    Amount,
    BusinessEntry,
    Entry,
    AbacusError,
)
from abacus.closing_types import ClosingEntry, CloseExpense, CloseIncome
from abacus.ledger import Ledger, Posting, process_postings
from abacus.ledger import OpenRegularAccount, OpenContraAccount


def yield_until(xs, classes):
    for x in xs:
        if any(isinstance(x, cls) for cls in classes):
            break
        yield x


class BaseJournal(BaseModel):
    open_regular_accounts: list[OpenRegularAccount] = []
    open_contra_accounts: list[OpenContraAccount] = []
    business_entries: list[Entry] = []
    adjustment_entries: list[Entry] = []
    closing_entries: list[ClosingEntry] = []
    post_close_entries: list[Entry] = []
    is_closed: bool = False

    def entries_for_closing_temp_contra_accounts(self):
        """Return close contra income and close contra expense accounts.
        Used to construct income statement."""

        def is_required(p):
            from abacus.closing_types import CloseContraExpense, CloseContraIncome

            return isinstance(p, CloseContraExpense) or isinstance(p, CloseContraIncome)

        return [p for p in self.closing_entries if is_required(p)]

    def yield_for_income_statement(self):
        entry_lists = [
            self.open_regular_accounts,
            self.open_contra_accounts,
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
            self.open_regular_accounts,
            self.open_contra_accounts,
            self.business_entries,
            self.adjustment_entries,
            self.closing_entries,
            self.post_close_entries,
        ]
        for entry_list in entry_lists:
            for entry in entry_list:
                yield entry

    def ledger(self):
        return process_postings(Ledger(), self.yield_all())

    def add_regular_accounts(self, ps: list[OpenRegularAccount]):
        self.open_regular_accounts.extend(ps)
        return self

    def add_contra_accounts(self, ps: list[OpenContraAccount]):
        self.open_contra_accounts.extend(ps)
        return self

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

        _gen = self.data.yield_for_income_statement()
        _ledger = process_postings(Ledger(), _gen)
        return income_statement(_ledger)

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
