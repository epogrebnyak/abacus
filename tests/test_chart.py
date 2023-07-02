import pytest

from abacus import Chart
from abacus.accounting_types import AbacusError, MultipleEntry
from abacus.book import starting_entry


def test_is_debit_account():
    assert (
        Chart(
            assets=["cash"],
            equity=[],
            expenses=[],
            liabilities=[],
            income=[],
        )
        .set_retained_earnings("re")
        .ledger()["cash"]
        .is_debit_account()
        is True
    )


def test_journal_with_starting_balance():
    chart = Chart(
        assets=["cash"],
        equity=["equity"],
        expenses=["salaries", "rent"],
        liabilities=[],
        income=["services"],
    ).set_retained_earnings("re")

    # Account balances are known from previous period end
    starting_balances = {"cash": 1400, "equity": 1500, "re": -100}
    assert starting_entry(chart.book(starting_balances)) == MultipleEntry(
        [("cash", 1400)],
        [("equity", 1500), ("re", -100)],
    )


chart = (
    Chart(
        assets=["cash", "receivables", "goods_for_sale", "ppe"],
        expenses=["cogs", "sga", "depreciation_expense"],
        equity=["equity"],
        liabilities=["dividend_due", "payables"],
        income=["sales"],
    )
    .set_retained_earnings("retained_earnings")
    .offset("ppe", ["depreciation"])
    .offset("sales", ["discount", "returned"])
)


def test_invalid_chart_with_duplicate_key():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash"],
            expenses=[],
            equity=["cash"],
            liabilities=[],
            income=[],
        ).set_retained_earnings("re")


def test_invalid_chart_with_non_existent_contra_account_name():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash", "goods"],
            expenses=["cogs"],
            equity=["capital"],
            liabilities=["loan"],
            income=["sales"],
        ).set_retained_earnings("re").offset("sssalessssss", ["refunds"])


def test_account_names_method():
    assert chart.account_names() == [
        "cash",
        "receivables",
        "goods_for_sale",
        "ppe",
        "cogs",
        "sga",
        "depreciation_expense",
        "equity",
        "dividend_due",
        "payables",
        "sales",
        "depreciation",
        "discount",
        "returned",
        "retained_earnings",
        "_profit",
    ]


def test_creation():
    (
        Chart(
            assets=["cash", "ar", "goods", "ppe"],
            equity=["equity", "retained_earnings"],
            income=["sales"],
            liabilities=["ap"],
            expenses=["cogs", "sga"],
        )
        .set_retained_earnings("retained_earnings")
        .offset("ppe", ["depreciation"])
        .offset("sales", ["refunds", "voids"])
        .set_name("ppe", "Property, plant, equipment")
        .set_name("goods", "Inventory (goods for sale)")
        .set_name("ar", "Accounts receivable")
        .set_name("ap", "Accounts payable")
        .set_name("cogs", "Cost of goods sold")
        .set_name("sga", "Selling, general and adm. expenses")
    )
    assert 1
