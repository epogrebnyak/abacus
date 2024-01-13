"""Command line interface using Typer package"""
import os
from dataclasses import dataclass
from pathlib import Path

from abacus.core import Chart
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


def get_store(store_file=None) -> LineJSON:
    return LineJSON.load()


def get_chart(chart_file: None = None) -> Chart:
    return UserChart.load(chart_file).chart()


def get_ledger(chart_file=None, store_file=None):
    chart = get_chart(chart_file)
    store = get_store(store_file)
    return chart.ledger().post_many(entries=store.yield_entries())


def get_ledger_income_statement(chart_file=None, store_file=None):
    chart = UserChart.load(chart_file).chart()
    store = LineJSON.load(store_file)
    ledger = chart.ledger()
    ledger.post_many(entries=store.yield_entries_for_income_statement(chart))
    return ledger


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
