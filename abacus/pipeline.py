from dataclasses import dataclass, field
from typing import List

from abacus.accounting_types import Entry, Posting
from abacus.closing import (
    closing_entries_for_permanent_contra_accounts,
    closing_entries_for_temporary_contra_accounts,
)
from abacus.ledger import Ledger, process_postings


@dataclass
class Pipeline:
    """Construct a list of postings to a ledger using add_entries() method
    and methods for closing accounts, run a pipeline to process all postings
    from a list.
    """

    start_ledger: Ledger
    postings: List[Posting] = field(default_factory=list)

    def add_entry(self, dr, cr, amount):
        entry = Entry(dr, cr, amount)
        self.postings.append(entry)
        return self

    def add_entries(self, entries: List[Entry]):
        self.postings.extend(entries)
        return self

    # not tested
    def close_income_and_expense_contra_accounts(self):
        self.postings.extend(closing_entries_for_temporary_contra_accounts(self.run()))
        return self

    def close_income_and_expense(self):
        pass
        return self

    def close_retained_earnings_account(self):
        pass
        return self

    def close(self):
        pass
        return self

    # not tested
    def close_permanent_contra_accounts(self):
        self.postings.extend(closing_entries_for_permanent_contra_accounts(self.run()))
        return self

    def create_ledger_for_balance_sheet(self):
        pass
        return self

    def create_ledger_for_income_statement(self):
        pass
        return self

    def run(self) -> Ledger:
        return process_postings(self.start_ledger, self.postings)
