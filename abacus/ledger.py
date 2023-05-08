"""General ledger."""

from collections import UserDict
from typing import List, Tuple

from .accounting_types import AccountName, Entry
from .accounts import Account, Asset, Capital, Expense, Income, Liability


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries) -> "Ledger":
        return process_entries(self, entries)

    def close_retained_earnings(
        self, retained_earnings_account_name: AccountName
    ) -> "Ledger":
        """Close income and expense accounts and move to
        profit or loss to retained earnigns"""
        from .closing import close

        return close(self, retained_earnings_account_name)

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


def assets(ledger):
    return subset_by_class(ledger, Asset)


def expenses(ledger):
    return subset_by_class(ledger, Expense)


def capital(ledger):
    return subset_by_class(ledger, Capital)


def liabilities(ledger):
    return subset_by_class(ledger, Liability)


def income(ledger):
    return subset_by_class(ledger, Income)


def process_entries(ledger: Ledger, entries: List[Entry]) -> Ledger:
    ledger, _failed_entries = safe_process_entries(ledger, entries)
    if _failed_entries:
        raise KeyError(_failed_entries)
    return ledger


def safe_process_entries(
    ledger: Ledger, entries: List[Entry]
) -> Tuple[Ledger, List[Entry]]:
    _ledger = ledger.safe_copy()
    _failed = []
    for entry in entries:
        try:
            _ledger[entry.dr].debit(entry.amount)
            _ledger[entry.cr].credit(entry.amount)
        except KeyError:
            _failed.append(entry)
    return _ledger, _failed
