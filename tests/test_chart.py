import pytest  # type: ignore

from abacus.engine.accounts import Asset, DebitAccount, RegularAccountEnum
from abacus.engine.base import AbacusError
from abacus.engine.chart import Chart
from abacus.engine.ledger import Ledger


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
        operations={},
        codes={},
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
    assert chart.viewer.account_names_all() == [
        "cash",
        "ar",
        "goods",
        "equity",
        "sales",
        "cogs",
        "sga",
        "refunds",
        "voids",
        "re",
        "current_profit",
        "null",
    ]


def test_contra_account_pairs(chart):
    assert list(chart.viewer.get_contra_account_pairs(RegularAccountEnum.INCOME)) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


def test_account_names(chart):
    assert chart.viewer.get_regular_account_names(Asset) == ["cash", "ar", "goods"]


def test_chart_offset_many():
    assert Chart(income=["sales"]).offset(
        "sales", ["refunds", "voids"]
    ).contra_accounts == dict(sales=["refunds", "voids"])


def test_chart_get_name():
    assert Chart().namer["_dividends_due"] == "Dividends due"


def test_chart_set_name_get_name():
    namer = Chart().set_name("cos", "Cost of sales").namer
    assert namer["cos"] == "Cost of sales"


def test_is_debit_account():
    acc = Ledger.new(
        Chart(
            assets=["cash"],
            equity=[],
            expenses=[],
            liabilities=[],
            income=[],
        )
    )["cash"]
    assert isinstance(acc, DebitAccount)


def test_offset():
    chart = Chart(
        assets=[],
        equity=[],
        expenses=[],
        liabilities=[],
        income=["sales"],
    ).offset("sales", "refund")
    assert chart.contra_accounts == {"sales": ["refund"]}
    chart.offset("sales", "voids")
    assert chart.contra_accounts == {"sales": ["refund", "voids"]}


chart = (
    Chart(
        assets=["cash", "receivables", "goods_for_sale", "ppe"],
        expenses=["cogs", "sga", "depreciation_expense"],
        equity=["equity"],
        liabilities=["dividend_due", "payables"],
        income=["sales"],
    )
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
        ).validate()


def test_invalid_chart_with_non_existent_contra_account_name():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash", "goods"],
            expenses=["cogs"],
            equity=["capital"],
            liabilities=["loan"],
            income=["sales"],
        ).offset("sssalessssss", ["refunds"])


def test_account_names_method(chart):
    assert chart.viewer.get_regular_account_names(Asset) == ["cash", "ar", "goods"]


def test_creation():
    (
        Chart(
            assets=["cash", "ar", "goods", "ppe"],
            equity=["equity", "retained_earnings"],
            income=["sales"],
            liabilities=["ap"],
            expenses=["cogs", "sga"],
        )
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
