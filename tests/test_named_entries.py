import pytest  # pylint: disable=import-error

from abacus.accounting_types import (
    BalanceSheet,
    Chart,
    Entry,
    IncomeStatement,
    NamedEntry,
    Shortcodes,
)


@pytest.fixture
def shortcodes():
    return Shortcodes(
        pay_shareholder_capital=("cash", "equity"),
        buy_goods_for_cash=("goods_for_sale", "cash"),
        invoice_buyer=("receivables", "sales"),
        transfer_goods_sold=("cogs", "goods_for_sale"),
        accept_payment=("cash", "receivables"),
        accrue_salary=("sga", "payables"),
        pay_salary=("payables", "cash"),
    )


@pytest.fixture
def named_entries():
    return [
        # start a company
        NamedEntry("pay_shareholder_capital", 501),
        NamedEntry("pay_shareholder_capital", 499),
        # acquire goods
        NamedEntry("buy_goods_for_cash", 820),
        # one order
        NamedEntry("invoice_buyer", 600),
        NamedEntry("transfer_goods_sold", 360),
        NamedEntry("accept_payment", 549),
        # pay labor
        NamedEntry("accrue_salary", 400),
        NamedEntry("pay_salary", 345),
        # another order
        NamedEntry("invoice_buyer", 160),
        NamedEntry("transfer_goods_sold", 80),
        NamedEntry("accept_payment", 80),
    ]


@pytest.fixture
def chart():
    return Chart(
        assets=["cash", "receivables", "goods_for_sale"],
        expenses=["cogs", "sga"],
        equity=["equity", "re"],
        liabilities=["divp", "payables"],
        income=["sales"],
    )


def test_named_entries():
    shortcodes = Shortcodes(pay_shareholder_capital=("cash", "equity"))
    assert shortcodes.make_entry(NamedEntry("pay_shareholder_capital", 200)) == Entry(
        "cash", "equity", 200
    )


def test_named_entries_income_statement(chart, shortcodes, named_entries):
    entries = shortcodes.make_entries(named_entries)
    ledger = chart.make_ledger().process_entries(entries)
    income_st = ledger.income_statement()
    assert income_st == IncomeStatement(
        income={"sales": 760}, expenses={"cogs": 440, "sga": 400}
    )


def test_named_entries_balance_sheet(chart, shortcodes, named_entries):
    entries = shortcodes.make_entries(named_entries)
    balance_st = (
        chart.make_ledger().process_entries(entries).close("re").balance_sheet()
    )
    assert balance_st == BalanceSheet(
        assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
        capital={"equity": 1000, "re": -80},
        liabilities={"divp": 0, "payables": 55},
    )
