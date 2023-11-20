import pytest
from composer import Chart # type: ignore

from abacus import Entry # type: ignore


@pytest.fixture
def closer0():
    chart = (
        Chart()
        .asset("cash")
        .capital("equity")
        .offset("equity", "ts")
        .name("ts", "Treasury stock")
        .asset("inventory")
        .expense("cogs")
        .income("sales")
        .offset("sales", "refunds")
    )
    ledger = (
        chart.ledger()
        .post("cash", "equity", 1000)
        .post("ts", "cash", 200)
        .post("inventory", "cash", 500)
        .post("cogs", "inventory", 60)
        .post("cash", "sales", 120)
        .post("refunds", "cash", 15)
        .post("refunds", "cash", 5)
    )

    return ledger.close()


def test_closing_entries_for_income_statement(closer0):
    assert closer0.closing_entries_for_income_statement() == [
        Entry(debit="sales", credit="refunds", amount=20)
    ]


def test_closing_entries_for_end_balances(closer0):
    assert closer0.closing_entries_for_end_balances() == [
        Entry(debit="sales", credit="refunds", amount=20),
        Entry(debit="sales", credit="current_profit", amount=100),
        Entry(debit="current_profit", credit="cogs", amount=60),
        Entry(debit="current_profit", credit="retained_earnings", amount=40),
    ]


def test_closing_entries_for_balance_sheet(closer0):
    assert closer0.closing_entries_for_balance_sheet() == [
        Entry(debit="sales", credit="refunds", amount=20),
        Entry(debit="sales", credit="current_profit", amount=100),
        Entry(debit="current_profit", credit="cogs", amount=60),
        Entry(debit="current_profit", credit="retained_earnings", amount=40),
        Entry(debit="equity", credit="ts", amount=200),
    ]


def test_ledger_post():
    chart0 = Chart().add("asset:cash").add("capital:equity").add("contra:equity:ts")
    assert chart0.ledger().post("cash", "equity", 1000).post(
        "ts", "cash", 200
    ).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}


def test_ledger_post_many():
    chart0 = Chart().asset("cash").capital("equity").offset("equity", "ts")
    assert chart0.ledger().post_many(
        [Entry("cash", "equity", 1000), Entry("ts", "cash", 200)]
    ).nonzero_balances() == {"cash": 800, "equity": 1000, "ts": 200}
