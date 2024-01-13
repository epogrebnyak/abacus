"""Command line interface using Typer package

Ideas:
- Allow bx without arguments to show help.

"""
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from abacus.entries_store import LineJSON
from abacus.user_chart import UserChart, make_user_chart


def last(label: str) -> str:
    return label.split(":")[-1]


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path(directory: Path | str | None = None) -> Path:
    if directory is None:
        directory = cwd()
    return Path(directory) / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


def get_store() -> LineJSON:
    return LineJSON(path=get_entries_path())


@dataclass
class UserChartCLI:
    user_chart: UserChart
    path: Path

    @classmethod
    def default(cls):
        path = get_chart_path()
        user_chart = make_user_chart()
        return cls(user_chart, path)

    @classmethod
    def load(cls, directory: Path | str | None = None):
        path = get_chart_path(directory)
        try:
            user_chart = UserChart.load(path)
        except FileNotFoundError:
            sys.exit(f"File not found: {path}. Use `init` command to create it.")
        return cls(user_chart, path)

    def save(self):
        return self.user_chart.save(path=self.path)


#     @property
#     def ledger(self):
#         return self.chart.ledger().post_many(entries=self.store.yield_entries())

#     # TODO: use rename_dict for viewers
#     def trial_balance(self):
#         return TrialBalance.new(self.ledger)

#     def balance_sheet(self):
#         return BalanceSheet.new(self.ledger)

#     def income_statement(self):
#         ledger = self.chart.ledger()
#         ledger.post_many(
#             entries=self.store.yield_entries_for_income_statement(self.chart)
#         )
#         return IncomeStatement.new(ledger)

#     def account_balances(self):
#         return self.ledger.balances
