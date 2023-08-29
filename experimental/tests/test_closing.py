from engine.accounts import Expense, Income
from engine.base import Amount, Entry
from engine.chart import Chart
from engine.closing import make_closing_entries
from engine.ledger import Ledger
from pytest import fixture


@fixture
def entries():
    doc_ = """
cash,equity,1000
goods,cash,800
cogs,goods,700
ar,sales,899
refunds,ar,89
cashback,ar,10
cash,ar,400
sga,cash,50"""

    def make(line):
        a, b, c = line.split(",")
        return Entry(a.strip(), b.strip(), Amount(c))

    return [make(line) for line in doc_.strip().split("\n")]


@fixture
def chart2():
    return Chart(
        assets=["cash", "goods", "ar"],
        equity=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        contra_accounts={"sales": ["refunds", "cashback"]},
    )


@fixture
def ledger_before_close(chart2, entries):
    return Ledger.new(chart2).post(entries)


def test_len_closing_entries(chart2, ledger_before_close):
    closing_entries = make_closing_entries(chart2, ledger_before_close)
    assert len(closing_entries.all()) == 6


def test_re_after_close(chart2, ledger_before_close):
    assert ledger_before_close.close(chart2).balances()["re"] == 50


def test_balances_after(chart2, ledger_before_close):
    assert ledger_before_close.close_some(chart2).subset(
        [Income, Expense]
    ).balances() == {
        "cogs": 700,
        "sga": 50,
        "sales": 800,
    }
