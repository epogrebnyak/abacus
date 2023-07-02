import pytest  # pylint: disable=import-error

from abacus.accounting_types import Entry
from abacus.chart import Chart


@pytest.fixture
def chart0():
    return Chart(
        assets=["cash", "receivables", "goods_for_sale"],
        expenses=["cogs", "sga"],
        equity=["equity"],
        liabilities=["divp", "payables"],
        income=["sales"],
    ).set_retained_earnings("re")


@pytest.fixture
def entries0():
    e1 = Entry(dr="cash", cr="equity", amount=1000)
    e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
    e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
    e4 = Entry(cr="sales", dr="cash", amount=400)
    e5 = Entry(cr="cash", dr="sga", amount=50)
    return [e1, e2, e3, e4, e5]
