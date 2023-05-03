"""
Classes for accounting.
"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass, field
from typing import List, Tuple

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
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


class Asset(DebitAccount):
    pass


class Expense(DebitAccount):
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

    def make_ledger(self):
        from .core import make_ledger

        return make_ledger(self)


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self):
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries):
        from .core import process_entries

        return process_entries(self, entries)

    def close(self, retained_earnings_account_name: AccountName):
        from .core import close

        return close(self, retained_earnings_account_name)

    def balances(self):
        from .core import balances

        return balances(self)

    def balance_sheet(self):
        from .core import balance_sheet

        return balance_sheet(self)

    def income_statement(self):
        from .core import income_statement

        return income_statement(self)


@dataclass
class BalanceSheet:
    assets: AccountBalancesDict
    capital: AccountBalancesDict
    liabilities: AccountBalancesDict

    def as_string(self, rename_dict=dict()):
        from .formatting import TextViewer

        return TextViewer(rename_dict).balance_sheet(self)


@dataclass
class IncomeStatement:
    income: AccountBalancesDict
    expenses: AccountBalancesDict

    def current_profit(self):
        return self.income.total() - self.expenses.total()

    def as_string(self, rename_dict=dict()):
        from .formatting import TextViewer

        return TextViewer(rename_dict).income_statement(self)


@dataclass
class NamedEntry:
    opcode: str
    amount: Amount


class Shortcodes(UserDict[str, Tuple[AccountName, AccountName]]):
    def make_entry(self, named_entry: NamedEntry) -> Entry:
        dr, cr = self[named_entry.opcode]
        return Entry(dr, cr, named_entry.amount)

    def make_entries(self, named_entries: List[NamedEntry]):
        return [self.make_entry(ne) for ne in named_entries]


TrialBalance = AccountBalancesDict
