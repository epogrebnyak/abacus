"""Command line interface using Typer package

Ideas:
- Allow bx without arguments to show help.

"""
import os
from dataclasses import dataclass
from pathlib import Path

from abacus.user_chart import UserChart


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


@dataclass
class UserChartCLI:
    user_chart: UserChart
    path: Path

    def offset(self, name: str, contra_name: str):
        self.user_chart.offset(name, contra_name)
        return self

    def name(self, name: str, title: str):
        self.user_chart.rename_dict[name] = title
        return self

    @classmethod
    def load(cls):
        path = get_chart_path()
        return cls(user_chart=UserChart.load(path), path=path)

    def save(self):
        return self.user_chart.save(path=self.path)


# @dataclass
# class Everything:
#     chart_path: Path = field(default_factory=get_chart_path)
#     entries_path: Path = field(default_factory=get_entries_path)

#     @property
#     def user_chart(self) -> UserChart:
#         return UserChart.load(path=self.chart_path)

#     @property
#     def chart(self) -> UserChart:
#         return self.user_chart.chart()

#     @property
#     def store(self) -> LineJSON:
#         return LineJSON(path=self.entries_path)

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
