# pylint: disable=import-error, no-member, missing-docstring, pointless-string-statement, invalid-name, redefined-outer-name

# Signatures:
# Chart -> Ledger -> [Entry] -> Ledger -> [Entry] -> Ledger
# Ledger -> (BalanceSheet, IncomeStatement) -> (Table, Table)
# Ledger -> TrialBalance
# TrialBalance -> Ledger # for reset of balances

from typing import Dict

from .accounting_types import AccountBalancesDict, Amount, BalanceSheet, IncomeStatement
from .ledger import Ledger, assets, capital, expenses, income, liabilities


def balances(ledger: Ledger) -> AccountBalancesDict:
    return AccountBalancesDict(
        {account_name: account.balance() for account_name, account in ledger.items()}
    )


def balance_sheet(ledger: Ledger) -> BalanceSheet:
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
        return rename_dict.get(s, s).capitalize().replace("_", " ")

    return AccountBalancesDict((mut(k), v) for k, v in balances_dict.items())
