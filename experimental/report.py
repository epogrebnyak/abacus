"""Income statement and balance sheet reports, created from ledger."""
# pylint: disable=missing-docstring
from typing import Dict

from engine import AccountName, Amount, Asset, Capital, Expense, Income, Liability
from pydantic import BaseModel  # pylint: disable=import-error # type: ignore


class BalanceSheet3(BaseModel):
    assets: Dict[str, int]

    @classmethod
    def _s(cls, ledger):
        return cls(assets=ledger.subset(Asset).balances())


class Report:
    pass


class BalanceSheet(BaseModel, Report):
    assets: Dict[AccountName, Amount]
    capital: Dict[AccountName, Amount]
    liabilities: Dict[AccountName, Amount]

    @classmethod
    def new(cls, ledger):
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
        return self.income.total() - self.expenses.total()
