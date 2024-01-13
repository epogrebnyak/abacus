"""Command line interface using Typer package

Ideas:
- Allow bx without arguments to show help.

"""
import os
from dataclasses import dataclass, field
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
class ChartCLI:
    path: Path = field(default_factory=get_chart_path)

    def user_chart(self):
        return UserChart.parse_file(self.path)


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
        user_chart = UserChart.load(path)
        return cls(user_chart, path)

    def save(self):
        return self.user_chart.save(path=self.path)


def get_ledger(chart_file: Path | None = None, store_file: Path | None = None):
    chart = UserChart.load(chart_file).chart()
    store = LineJSON.load(store_file)
    return chart.ledger().post_many(entries=store.yield_entries())


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
