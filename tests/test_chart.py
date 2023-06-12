import pytest

from abacus import Chart
from abacus.accounting_types import AbacusError, MultipleEntry
from abacus.book import starting_entry


def test_is_debit_account():
    assert (
        Chart(
            assets=["cash"],
            equity=[],
            retained_earnings_account="",
            expenses=[],
            liabilities=[],
            income=[],
        ).is_debit_account("cash")
        is True
    )


def test_journal_with_starting_balance():
    chart = Chart(
        assets=["cash"],
        equity=["equity"],
        retained_earnings_account="re",
        expenses=["salaries", "rent"],
        liabilities=[],
        income=["services"],
    )
    # Account balances are known from previous period end
    starting_balances = {"cash": 1400, "equity": 1500, "re": -100}
    assert starting_entry(chart.book(starting_balances)) == MultipleEntry(
        [("cash", 1400)],
        [("equity", 1500), ("re", -100)],
    )


chart = Chart(
    assets=["cash", "receivables", "goods_for_sale", "ppe"],
    expenses=["cogs", "sga", "depreciation_expense"],
    equity=["equity"],
    retained_earnings_account="retained_earnings",
    liabilities=["dividend_due", "payables"],
    income=["sales"],
    contra_accounts={
        "ppe": ["depreciation"],
        "sales": ["discount", "returned"],
    },
)


def test_invalid_chart_with_duplicate_key():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash"],
            expenses=[],
            equity=["cash"],
            retained_earnings_account="re",
            liabilities=[],
            income=[],
        )


def test_invalid_chart_with_non_existent_contra_account_name():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash", "goods"],
            expenses=["cogs"],
            equity=["capital"],
            retained_earnings_account="re",
            liabilities=["loan"],
            income=["sales"],
            contra_accounts={"sssalessssss": []},
        )


def test_account_names_method():
    assert chart.account_names == [
        "cash",
        "receivables",
        "goods_for_sale",
        "ppe",
        "cogs",
        "sga",
        "depreciation_expense",
        "equity",
        "retained_earnings",
        "dividend_due",
        "payables",
        "sales",
        "_profit",
        "depreciation",
        "discount",
        "returned",
    ]
