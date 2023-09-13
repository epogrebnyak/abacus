from engine.accounts import Expense, Income
from engine.base import Amount, Entry
from engine.chart import Chart
from engine.closing import make_closing_entries
from engine.ledger import Ledger
from pytest import fixture  # type: ignore


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
    return Ledger.new(chart2).post_many(entries)


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


from engine.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraIncome,
    RetainedEarnings,
    Liability,
    IncomeSummaryAccount,
    Expense,
    Income,
)


def test_closing_entries():
    chart = (
        Chart(
            assets=["cash", "receivables", "goods_for_sale", "ppe"],
            expenses=["cogs", "sga", "depreciation_expense"],
            equity=["equity"],
            liabilities=["dividend_due", "payables"],
            income=["sales"],
        )
        .offset("ppe", ["depreciation"])
        .offset("sales", ["discount", "returns"])
    )

    ledger = Ledger(
        {
            "cash": Asset(debits=[4000, 620], credits=[3000, 250, 40, 25, 50]),
            "goods_for_sale": Asset(debits=[250], credits=[180]),
            "ppe": Asset(
                debits=[3000],
                credits=[],
            ),
            "cogs": Expense(debits=[180], credits=[]),
            "sga": Expense(debits=[50], credits=[]),
            "depreciation_expense": Expense(debits=[250], credits=[]),
            "equity": Capital(debits=[], credits=[4000]),
            "re": RetainedEarnings(debits=[], credits=[]),
            "divp": Liability(debits=[], credits=[]),
            "sales": Income(
                debits=[],
                credits=[620],
            ),
            "depreciation": ContraAsset(debits=[], credits=[250]),
            "discount": ContraIncome(debits=[40, 25], credits=[]),
            "returns": ContraIncome(debits=[], credits=[]),
            "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
        }
    )

    assert list(make_closing_entries(chart, ledger).all()) == [
        Entry(debit="sales", credit="discount", amount=65),
        Entry(debit="sales", credit="returns", amount=0),
        Entry(debit="sales", credit="current_profit", amount=555),
        Entry(debit="current_profit", credit="cogs", amount=180),
        Entry(debit="current_profit", credit="sga", amount=50),
        Entry(debit="current_profit", credit="depreciation_expense", amount=250),
        Entry(debit="current_profit", credit="re", amount=75),
    ]
