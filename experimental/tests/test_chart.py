import pytest
from engine.accounts import Asset, Income
from engine.base import AbacusError
from engine.chart import Chart


def test_empty_chart_constructor():
    assert Chart().dict() == dict(
        assets=[],
        expenses=[],
        equity=[],
        liabilities=[],
        income=[],
        retained_earnings_account="re",
        income_summary_account="current_profit",
        null_account="null",
        contra_accounts={},
        names={"re": "Retained earnings"},
    )


def test_chart_duplicates():
    with pytest.raises(AbacusError):
        Chart(assets=["cash"]).offset("cash", "cash").validate()


def test_chart_offset_does_not_exist():
    with pytest.raises(AbacusError):
        Chart().offset("account", "contra_account")


def test_chart_offset():
    assert Chart(income=["sales"]).offset("sales", "refunds").contra_accounts == dict(
        sales=["refunds"]
    )


def test_accounts_names_all(chart):
    assert chart.account_names_all() == [
        "cash",
        "ar",
        "goods",
        "cogs",
        "sga",
        "equity",
        "sales",
        "refunds",
        "voids",
        "re",
        "current_profit",
        "null",
    ]


def test_contra_account_pairs(chart):
    assert list(chart.contra_account_pairs(Income)) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


def test_account_names(chart):
    assert chart.account_names(Asset) == ["cash", "ar", "goods"]


def test_chart_offset_many():
    assert Chart(income=["sales"]).offset(
        "sales", ["refunds", "voids"]
    ).contra_accounts == dict(sales=["refunds", "voids"])


def test_chart_get_name():
    assert Chart().get_name("_dividends_due") == "Dividends due"


def test_chart_set_name_get_name():
    assert Chart().set_name("cos", "Cost of sales").get_name("cos") == "Cost of sales"
