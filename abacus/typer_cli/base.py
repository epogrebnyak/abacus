"""Command line interface using Typer package"""
import os
from pathlib import Path

from abacus.core import Chart
from abacus.entries_store import LineJSON
from abacus.user_chart import UserChart


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
