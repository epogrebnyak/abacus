"""Navigation for cli."""

from abacus.core import Chart, Ledger
from abacus.entries_store import LineJSON
from abacus.user_chart import UserChart


def last(label: str) -> str:
    return label.split(":")[-1]

def get_store(store_file=None) -> LineJSON:
    return LineJSON.load(store_file)


def get_chart(chart_file = None) -> Chart:
    return UserChart.load(chart_file).chart()


def get_ledger(chart_file=None, store_file=None):
    chart = get_chart(chart_file)
    store = get_store(store_file)
    return chart.ledger().post_many(entries=store.yield_entries())


def get_ledger_income_statement(chart_file=None, store_file=None):
    chart = get_chart(chart_file)
    store = get_store(store_file)
    ledger = chart.ledger()
    ledger.post_many(entries=store.yield_entries_for_income_statement(chart))
    return ledger
