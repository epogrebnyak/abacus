from chart import Chart
from ledger import Ledger
from base import Entry
from pytest import fixture


@fixture
def chart():
    return Chart(
        assets=["cash", "ar", "goods"],
        equity=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        contra_accounts={"sales": ["refunds", "voids"]},
    )


@fixture
def ledger(chart):
    return Ledger.new(chart).post(
        [
            Entry("cash", "equity", 1000),
            Entry("ar", "sales", 250),
            Entry("refunds", "ar", 50),
        ]
    )
