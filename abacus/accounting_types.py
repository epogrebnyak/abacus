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
from dataclasses import dataclass, field
from typing import List, Tuple, Optional



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


@dataclass
class Netting:
    contra_accounts: List[AccountName]
    target_name: AccountName


@dataclass
class Account:
    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    def balance(self) -> Amount:
        raise NotImplementedError

    def debit(self, amount: Amount):
        self.debits.append(amount)

    def credit(self, amount: Amount):
        self.credits.append(amount)

    def safe_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())


@dataclass
class RegularAccount(Account):
    netting: Optional[Netting] = None


class DebitAccount(Account):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(Account):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


class Asset(DebitAccount, RegularAccount):
    pass


class Expense(DebitAccount, RegularAccount):
    pass


class Capital(CreditAccount, RegularAccount):
    pass


class Liability(CreditAccount, RegularAccount):
    pass


class Income(CreditAccount, RegularAccount):
    pass


class IncomeSummaryAccount(CreditAccount):
    pass


class ContraAccount:
    pass


class DebitContraAccount(DebitAccount, ContraAccount):
    pass


class CreditContraAccount(CreditAccount, ContraAccount):
    pass


@dataclass
class Chart:
    """Chart of accounts."""

    assets: List[str]
    expenses: List[str]
    equity: List[str]
    liabilities: List[str]
    income: List[str]
    debit_contra_accounts: List[Tuple[str, str]] = field(default_factory=list)
    credit_contra_accounts: List[Tuple[str, str]] = field(default_factory=list)
    income_summary_account: str = "profit"

    # TODO: must check for duplicatre account keys

    def _is_debit_account(self, account_name):
        return account_name in self.assets + self.expenses

    def _is_credit_account(self, account_name):
        return account_name in self.equity + self.liabilities + self.income

    def __post_init__(self):
        for account_name, nets_with in self.debit_contra_accounts:
            if not self._is_credit_account(nets_with):
                raise ValueError(
                    f"contra account {account_name} must match credit account,"
                    f"{nets_with} is not credit account"
                )
        for account_name, nets_with in self.credit_contra_accounts:
            if not self._is_debit_account(nets_with):
                raise ValueError(
                    f"contra account {account_name} must match debit account,"
                    f"{nets_with} is not debit account"
                )

    def make_ledger(self):
        from .core import make_ledger

        return make_ledger(self)


class Ledger(UserDict[AccountName, Account]):
    """General ledger that holds all accounts."""

    def safe_copy(self) -> "Ledger":
        return Ledger((k, account.safe_copy()) for k, account in self.items())

    def process_entries(self, entries) -> "Ledger":
        from .core import process_entries

        return process_entries(self, entries)

    def close_retained_earnings(
        self, retained_earnings_account_name: AccountName
    ) -> "Ledger":
        """Close income and expense accounts and move to
        profit or loss to retained earnigns"""
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
