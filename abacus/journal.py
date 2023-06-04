from collections import UserList
from typing import List

from abacus.accounting_types import AccountName, Amount, BusinessEntry
from abacus.closing_types import CloseExpense, CloseIncome
from abacus.ledger import Ledger, Posting, process_postings


def yield_until(xs, classes):
    for x in xs:
        if any(isinstance(x, cls) for cls in classes):
            break
        yield x


class Journal(UserList[Posting]):
    """A list of postings."""

    # def is_closed(self) -> bool:
    #     # - income and expense contra accounts are zero
    #     # - income and expense accounts are zero
    #     # - isa is zero
    #     raise NotImplementedError

    @classmethod
    def from_file(cls, path) -> "Journal":
        raise NotImplementedError

    def post_many(self, entries: List[Posting]) -> "Journal":
        self.data.extend(entries)
        return self

    def post(self, dr: AccountName, cr: AccountName, amount: Amount) -> "Journal":
        entry = BusinessEntry(dr, cr, amount)
        return self.post_many([entry])

    def adjust(self, dr, cr, amount) -> "Journal":
        raise NotImplementedError

    def post_close(self, dr, cr, amount) -> "Journal":
        raise NotImplementedError

    def close(self) -> "Journal":
        from abacus.closing import closing_entries

        self.post_many(closing_entries(self.ledger()))  # type: ignore
        return self

    def current_profit(self):
        return self.income_statement().current_profit()

    def ledger(self):
        return process_postings(Ledger(), self.data)

    def balances(self):
        from .reports import balances

        return balances(self.ledger())

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self.ledger())

    def income_statement(self):
        from .reports import income_statement

        _gen = yield_until(self.data, [CloseExpense, CloseIncome])
        _ledger = process_postings(Ledger(), _gen)
        return income_statement(_ledger)
