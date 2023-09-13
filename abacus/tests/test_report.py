import pytest  # type: ignore

from abacus import BalanceSheet, Chart, Entry, IncomeStatement, Ledger


def test_create_balance_sheet():
    chart = Chart(assets=["cash"], equity=["equity"])
    ledger = Ledger.new(chart).post(Entry("cash", "equity", 1000))
    assert ledger.balance_sheet(chart) == BalanceSheet(
        assets={"cash": 1000}, capital={"equity": 1000, "re": 0}, liabilities={}
    )


@pytest.fixture
def chart0():
    return Chart(
        assets=["cash", "receivables", "goods_for_sale"],
        expenses=["cogs", "sga"],
        equity=["equity"],
        liabilities=["divp", "payables"],
        income=["sales"],
    )


@pytest.fixture
def entries0():
    e1 = Entry(debit="cash", credit="equity", amount=1000)
    e2 = Entry(debit="goods_for_sale", credit="cash", amount=250)
    e3 = Entry(credit="goods_for_sale", debit="cogs", amount=200)
    e4 = Entry(credit="sales", debit="cash", amount=400)
    e5 = Entry(credit="cash", debit="sga", amount=50)
    return [e1, e2, e3, e4, e5]


def test_income_statement(chart0, entries0):
    income_st = chart0.ledger().post_many(entries0).income_statement(chart0)
    assert income_st == IncomeStatement(
        income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
    )


def test_balance_sheet_with_close(chart0, entries0):
    balance_st = chart0.ledger().post_many(entries0).balance_sheet(chart0)
    assert balance_st == BalanceSheet(
        assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
        capital={"equity": 1000, "re": 150},
        liabilities={"divp": 0, "payables": 0},
    )


def test_balances(chart0, entries0):
    assert chart0.ledger().post_many(entries0).close(chart0).balances() == {
        "cash": 1100,
        "receivables": 0,
        "goods_for_sale": 50,
        "cogs": 0,
        "sga": 0,
        "equity": 1000,
        "re": 150,
        "divp": 0,
        "payables": 0,
        "sales": 0,
        "current_profit": 0,
        "null": 0,
    }
