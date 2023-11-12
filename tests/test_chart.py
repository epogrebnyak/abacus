import pytest  # type: ignore

from abacus.engine.accounts import Asset, DebitAccount
from abacus.engine.base import AbacusError
from abacus.engine.better_chart import BaseChart, Chart


def test_empty_chart_constructor():
    assert Chart().dict() == {
        "base_chart": {
            "assets": [],
            "expenses": [],
            "capital": [],
            "liabilities": [],
            "income": [],
            "income_summary_account": "",
            "retained_earnings_account": "",
            "contra_accounts": {},
            "null_account": "",
        },
        "titles": {},
        "operations": {},
    }


def test_chart_duplicates():
    with pytest.raises(AbacusError):
        Chart(assets=["cash"]).offset("cash", "cash").validate()


def test_chart_offset_does_not_exist():
    with pytest.raises(AbacusError):
        Chart().offset("account", "contra_account")


def test_chart_offset():
    assert Chart().add("income:sales").offset(
        "sales", "refunds"
    ).base_chart.contra_accounts == dict(sales=["refunds"])


@pytest.mark.skip
def test_accounts_names_all(chart):
    assert [name.account_name for name in chart.base_chart.yield_names()] == [
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
    from abacus.engine.better_chart import IncomeName

    assert list(chart.base_chart.yield_contra_account_pairs(IncomeName)) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


def test_account_names(chart):
    assert list(chart.base_chart.filter_accounts([Asset])) == ["cash", "ar", "goods"]


def test_chart_offset_many():
    assert Chart().add("income:sales").offset_many(
        "sales", ["refunds", "voids"]
    ).base_chart.contra_accounts == dict(sales=["refunds", "voids"])


def test_chart_get_name():
    assert Chart().get_title("_dividends_due") == "Dividends due"


def test_chart_set_name_get_name():
    assert Chart().name("cos", "Cost of sales").get_title("cos") == "Cost of sales"


def test_is_debit_account():
    acc = Chart().asset("cash").ledger()["cash"]
    assert isinstance(acc, DebitAccount)


def test_offset():
    chart = Chart().income("sales").offset("sales", "refund")
    assert chart.base_chart.contra_accounts == {"sales": ["refund"]}
    chart.offset("sales", "voids")
    assert chart.base_chart.contra_accounts == {"sales": ["refund", "voids"]}


chart = (
    Chart(
        base_chart=BaseChart(
            assets=["cash", "receivables", "goods_for_sale", "ppe"],
            expenses=["cogs", "sga", "depreciation_expense"],
            capital=["equity"],
            liabilities=["dividend_due", "payables"],
            income=["sales"],
        )
    )
    .offset("ppe", "depreciation")
    .offset_many("sales", ["discount", "returned"])
)


def test_invalid_chart_with_non_existent_contra_account_name():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash", "goods"],
            expenses=["cogs"],
            capital=["capital"],
            liabilities=["loan"],
            income=["sales"],
        ).offset("sssalessssss", ["refunds"])


def test_creation():
    assert (
        Chart(
            base_chart=BaseChart(
                assets=["cash", "ar", "goods", "ppe"],
                capital=["equity", "retained_earnings"],
                income=["sales"],
                liabilities=["ap"],
                expenses=["cogs", "sga"],
            )
        )
        .offset("ppe", "depreciation")
        .offset_many("sales", ["refunds", "voids"])
        .name("ppe", "Property, plant, equipment")
        .name("goods", "Inventory (goods for sale)")
        .name("ar", "Accounts receivable")
        .name("ap", "Accounts payable")
        .name("cogs", "Cost of goods sold")
        .name("sga", "Selling, general and adm. expenses")
    )
