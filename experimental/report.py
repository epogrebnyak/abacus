# pylint: disable=missing-docstring
from typing import Dict

from engine import AccountName, Amount, Asset, Capital, Expense, Income, Liability
from pydantic import BaseModel  # pylint: disable=import-error # type: ignore


class Report:
    pass


def total(dict_) -> Amount:
    return sum(dict_.values())


class BalanceSheet(BaseModel, Report):
    assets: Dict[AccountName, Amount]
    capital: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger) -> "BalanceSheet":
        return BalanceSheet(
            assets=ledger.subset(Asset).balances(),
            capital=ledger.subset(Capital).balances(),
            liabilities=ledger.subset(Liability).balances(),
        )


class IncomeStatement(BaseModel, Report):
    income: Dict[AccountName, Amount]
    expenses: Dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger) -> "IncomeStatement":
        return IncomeStatement(
            income=ledger.subset(Income).balances(),
            expenses=ledger.subset(Expense).balances(),
        )

    def current_profit(self):
        return total(self.income) - total(self.expenses)
