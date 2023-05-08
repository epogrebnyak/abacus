"""
Classes for a minimal accounting framework.

Simplifying assumptions:

- flat ledger, no subaccounts
- no contraccounts (eg depreciation)
- one currency
- no journals, entries posted directly to ledger
- entry holds amount, dr and cr account, no title or date
- no compound entries, entry affects exacly two accounts
- only balance sheet and income statement reports 
- flat income statement (just income and expenses)
- little checks (eg can distribute dividend greater than profit)
- account has either debit side balance or credit side balance, 
  balances do not migrate
- all accounts permanent, no temporary accounts 

"""

# pylint: disable=no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass
from typing import List, Tuple

Amount = int
AccountName = str


@dataclass
class Entry:
    """Accounting entry with amount and account names to be debited (dr)
    and credited (cr)."""

    dr: AccountName
    cr: AccountName
    amount: Amount


class AccountBalancesDict(UserDict[AccountName, Amount]):
    """Dictionary with account names and balances, example:
    AccountBalancesDict({'cash': 100})
    """

    def total(self) -> Amount:
        return sum(self.values())


class Report:
    pass


@dataclass
class BalanceSheet(Report):
    assets: AccountBalancesDict
    capital: AccountBalancesDict
    liabilities: AccountBalancesDict


@dataclass
class IncomeStatement(Report):
    income: AccountBalancesDict
    expenses: AccountBalancesDict

    def current_profit(self):
        return self.income.total() - self.expenses.total()


@dataclass
class NamedEntry:
    opcode: str
    amount: Amount


"""Pair of debit and credit account names."""
Pair = Tuple[AccountName, AccountName]


class Shortcodes(UserDict[str, Pair]):
    """A dictionary that holds names of typical entry templates (pairs).
    Methods allow to convert NamedEntry("pay_capital", 1000) to
    Entry("cash", "capital", 1000) for a single entry or a list of entries.
    """

    def make_entry(self, named_entry: NamedEntry) -> Entry:
        dr, cr = self[named_entry.opcode]
        return Entry(dr, cr, named_entry.amount)

    def make_entries(self, named_entries: List[NamedEntry]):
        return [self.make_entry(ne) for ne in named_entries]


TrialBalance = AccountBalancesDict


@dataclass
class Saldo:
    """Account name and balance.

    Note: 'saldo' in balance in Italian."""

    account_name: AccountName
    amount: Amount
