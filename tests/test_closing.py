from pytest import fixture  # type: ignore

from abacus.engine.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)
from abacus.engine.base import Entry
from abacus.engine.better_chart import BaseChart, Chart
from abacus.engine.closing import make_closing_entries
from abacus.engine.ledger import Ledger


@fixture
def entries():
    return [
        Entry(debit="cash", credit="equity", amount=1000),
        Entry(debit="goods", credit="cash", amount=800),
        Entry(debit="cogs", credit="goods", amount=700),
        Entry(debit="ar", credit="sales", amount=899),
        Entry(debit="refunds", credit="ar", amount=89),
        Entry(debit="cashback", credit="ar", amount=10),
        Entry(debit="cash", credit="ar", amount=400),
        Entry(debit="sga", credit="cash", amount=50),
    ]


@fixture
def chart2():
    return Chart(
        base_chart=BaseChart(
            assets=["cash", "goods", "ar"],
            capital=["equity"],
            income=["sales"],
            expenses=["cogs", "sga"],
            contra_accounts={"sales": ["refunds", "cashback"]},
            retained_earnings_account="re",
            null_account="null",
            income_summary_account="current_profit",
        )
    )


@fixture
def ledger_before_close(chart2, entries):
    return chart2.ledger().post_many(entries)


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


def test_closing_entries():
    chart = (
        Chart(
            base_chart=BaseChart(
                assets=["cash", "receivables", "goods_for_sale", "ppe"],
                expenses=["cogs", "sga", "depreciation_expense"],
                capital=["equity"],
                liabilities=["dividend_due", "payables"],
                income=["sales"],
                retained_earnings_account="re",
                null_account="null",
                income_summary_account="current_profit",
            )
        )
        .offset("ppe", "depreciation")
        .offset_many("sales", ["discount", "returns"])
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
