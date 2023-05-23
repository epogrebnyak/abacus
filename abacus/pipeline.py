from dataclasses import dataclass, field
from typing import List

from abacus.accounting_types import Entry, Posting
from abacus.closing import (
    closing_entries_for_permanent_contra_accounts,
    closing_entries_for_temporary_contra_accounts,
    closing_entries_income_and_expense_to_isa,
    closing_entry_isa_to_retained_earnings,
)
from abacus.ledger import Ledger, process_postings


@dataclass
class Pipeline:
    """Construct a list of postings to a ledger using add_entries() method
    and methods for closing accounts, run a pipeline to process all postings
    from a list.

    Note: one may create a Pipeline before period end and add a ledger with regular
    entries to keep down the load of re-computing the pipeline.
    """

    start_ledger: Ledger
    postings: List[Posting] = field(default_factory=list)

    def add_entry(self, dr, cr, amount):
        entry = Entry(dr, cr, amount)
        self.postings.append(entry)
        return self

    def extend(self, postings):
        self.postings.extend(postings)
        return self

    def add_entries(self, entries: List[Entry]):
        return self.extend(entries)

    # FIXME: not tested
    def close_income_and_expense_contra_accounts(self):
        more_postings = closing_entries_for_temporary_contra_accounts(ledger=self.run())
        return self.extend(more_postings)

    # FIXME: not tested
    def close_income_and_expense(self):
        more_postings = closing_entries_income_and_expense_to_isa(ledger=self.run())
        return self.extend(more_postings)

    # FIXME: not tested
    def close_retained_earnings_account(self):
        more_postings = closing_entry_isa_to_retained_earnings(ledger=self.run())
        return self.extend(more_postings)

    # FIXME: not tested
    def close(self):
        self.close_income_and_expense_contra_accounts()
        self.close_income_and_expense()
        self.close_retained_earnings_account()
        return self

    # FIXME: not tested
    def close_permanent_contra_accounts(self):
        more_postings = closing_entries_for_permanent_contra_accounts(ledger=self.run())
        return self.extend(more_postings)

    # WONTFIX
    def get_ledger_for_balance_sheet(self):
        pass

    # WONTFIX
    def get_ledger_for_income_statement(self):
        pass
        return self

    def run(self) -> Ledger:
        return process_postings(self.start_ledger, self.postings)
