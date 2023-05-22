"""General ledger."""

from collections import UserDict
from typing import List, Tuple

from .accounting_types import AccountName, Entry, Posting, RenameAccount
from .accounts import Account, Asset, Capital, Expense, Income, Liability


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries) -> "Ledger":
        return process_postings(self, entries)

    def process_entry(self, dr, cr, amount) -> "Ledger":
        return process_postings(self, [Entry(dr, cr, amount)])

    def close(self) -> "Ledger":
        """Close contraaccounts, associated with income and expense accounts,
        aggregate profit or loss at income summary account
        and move balance of income summary account to retained earnings."""
        from .closing import close

        return close(self)

    def balances(self):
        from .reports import balances

        return balances(self)

    def balance_sheet(self):
        from .reports import balance_sheet

        return balance_sheet(self)

    def income_statement(self):
        from .reports import income_statement

        return income_statement(self)


def subset_by_class(ledger, cls):
    return Ledger(
        (account_name, account)
        for account_name, account in ledger.items()
        if isinstance(account, cls)
    )


def assets(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Asset)


def expenses(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Expense)


def capital(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Capital)


def liabilities(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Liability)


def income(ledger: Ledger) -> Ledger:
    return subset_by_class(ledger, Income)


def process_postings(ledger: Ledger, postings: List[Posting]) -> Ledger:
    ledger, _failed_entries = safe_process_postings(ledger, postings)
    if _failed_entries:
        raise KeyError(_failed_entries)
    return ledger


def _process(ledger: Ledger, posting: Posting) -> Ledger:
    match posting:
        case Entry(dr, cr, amount):
            ledger[dr].debits.append(amount)
            ledger[cr].credits.append(amount)
        case RenameAccount(existing_name, new_name):
            ledger[new_name] = ledger[existing_name].safe_copy()
            del ledger[existing_name]
    return ledger


def safe_process_postings(
    ledger: Ledger, postings: List[Posting]
) -> Tuple[Ledger, List[Posting]]:
    _ledger = ledger.safe_copy()
    _failed = []
    for posting in postings:
        try:
            _ledger = _process(_ledger, posting)
        except KeyError:
            _failed.append(posting)
    return _ledger, _failed
