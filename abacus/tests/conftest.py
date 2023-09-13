import pytest  # type: ignore
from pytest import fixture  # type: ignore

from abacus.engine.base import Entry
from abacus.engine.chart import Chart
from abacus.engine.ledger import Ledger


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
    return Ledger.new(chart).post_many(
        [
            Entry("cash", "equity", 1000),
            Entry("ar", "sales", 250),
            Entry("refunds", "ar", 50),
        ]
    )


@pytest.fixture
def entries():
    e1 = Entry(debit="cash", credit="equity", amount=1000)
    e2 = Entry(debit="goods", credit="cash", amount=250)
    e3 = Entry(debit="cogs", credit="goods", amount=200)
    e4 = Entry(debit="cash", credit="sales", amount=400)
    e5 = Entry(debit="sga", credit="cash", amount=50)
    return [e1, e2, e3, e4, e5]
