# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from dataclasses import dataclass
from typing import Dict
from collections import UserDict

from .accounting_types import AccountName, Amount
from .ledger import Ledger, assets, capital, expenses, income, liabilities
from .closing import closing_entries_for_permanent_contra_acounts


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


def balance_sheet(ledger: Ledger) -> BalanceSheet:
    # Note: must be closed ledger, may check.
    entries = closing_entries_for_permanent_contra_acounts(ledger)
    ledger = ledger.process_entries(entries)
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


def rename_keys(
    balances_dict: AccountBalancesDict, rename_dict: Dict
) -> AccountBalancesDict:
    def mut(s):
        return rename_dict.get(s, s).replace("_", " ").strip().capitalize()

    return AccountBalancesDict((mut(k), v) for k, v in balances_dict.items())