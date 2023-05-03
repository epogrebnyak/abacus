"""
Classes for accounting.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass, field
from typing import List

Amount = int
AccountName = str


@dataclass
class Entry:
    """Accounting entry with account names to be debited (dr)
    and credited (cr) and amount."""

    dr: AccountName
    cr: AccountName
    amount: Amount


class ClosingEntry(Entry):
    """Same as entry, used to close accounts at accounting period end."""

    pass


class AccountBalancesDict(UserDict[AccountName, Amount]):
    """Dictionary with account names and balances like {'cash': 100}."""

    def total(self) -> Amount:
        return sum(self.values())


@dataclass
class Account:
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)

    def safe_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


class DebitAccount(Account):
    pass


class Asset(DebitAccount):
    pass


class Expense(DebitAccount):
    pass


class CreditAccount(Account):
    pass


class Capital(CreditAccount):
    pass


class Liability(CreditAccount):
    pass


class Income(CreditAccount):
    pass


class IncomeSummaryAccount(CreditAccount):
    pass


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]
    contraccounts: List[str] = field(default_factory=list)
    income_summary_account: str = "profit"


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self):
        return Ledger((k, account.safe_copy()) for k, account in self.items())


@dataclass
class BalanceSheet:
    assets: AccountBalancesDict
    capital: AccountBalancesDict
    liabilities: AccountBalancesDict

    def is_valid(self):
        return self.assets.total() == self.capital.total() + self.liabilities.total()


@dataclass
class IncomeStatement:
    income: AccountBalancesDict
    expenses: AccountBalancesDict

    def current_profit(self):
        return self.income.total() - self.expenses.total()


TrialBalance = AccountBalancesDict
