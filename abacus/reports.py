# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from collections import UserDict
from dataclasses import dataclass

from abacus.accounting_types import AccountName, Amount
from abacus.closing import closing_entries_for_permanent_contra_accounts

from .ledger import Ledger, assets, capital, expenses, income, liabilities

__all__ = ["BalanceSheet", "IncomeStatement"]


class AccountBalancesDict(UserDict[AccountName, Amount]):
    """Dictionary with account names and balances, example:
    AccountBalancesDict({'cash': 100})
    """

    def total(self) -> Amount:
        return sum(self.values())


TrialBalance = AccountBalancesDict


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


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        {account_name: account.balance() for account_name, account in ledger.items()}
    )


def balance_sheet(ledger: Ledger, netting) -> BalanceSheet:
    entries = closing_entries_for_permanent_contra_accounts(ledger, netting)
    ledger = ledger.process_postings(entries)
    return BalanceSheet(
        assets=balances(assets(ledger)),
        capital=balances(capital(ledger)),
        liabilities=balances(liabilities(ledger)),
    )


def income_statement(ledger: Ledger) -> IncomeStatement:
    return IncomeStatement(
        income=balances(income(ledger)),
        expenses=balances(expenses(ledger)),
    )


def current_profit(ledger: Ledger) -> Amount:
    return income_statement(ledger).current_profit()
