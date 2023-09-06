from engine.base import Entry
from engine.chart import Chart
from engine.ledger import Ledger
from pytest import fixture  # type: ignore


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
