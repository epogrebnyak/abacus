# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

from typing import Dict

from .accounting_types import AccountBalancesDict, Amount, BalanceSheet, IncomeStatement
from .ledger import Ledger, assets, capital, expenses, income, liabilities
from .closing import close_permanent_contra_acounts


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        {account_name: account.balance() for account_name, account in ledger.items()}
    )


def balance_sheet(ledger: Ledger) -> BalanceSheet:
    ledger = close_permanent_contra_acounts(ledger)
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
