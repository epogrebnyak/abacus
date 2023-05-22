import pytest

from abacus import Chart
from abacus.accounting_types import AbacusError
from abacus.accounts import (
    Asset,
    Capital,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale", "ppe"],
    expenses=["cogs", "sga", "depreciation_expense"],
    equity=["equity", "retained_earnings"],
    liabilities=["dividend_due", "payables"],
    income=["sales"],
    contra_accounts={
        "ppe": (["depreciation"], "net_ppe"),
        "sales": (["discount", "returned"], "net_sales"),
    },
)


def test_invalid_chart():
    with pytest.raises(AbacusError):
        Chart(
            assets=["cash"],
            expenses=[],
            equity=["cash"],
            liabilities=[],
            income=[],
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
    ]


def test_chart_flat():
    assert chart.set_retained_earnings_account("retained_earnings")._flat() == [
        (Asset, ["cash", "receivables", "goods_for_sale", "ppe"]),
        (Expense, ["cogs", "sga", "depreciation_expense"]),
        (Capital, ["equity"]),
        (Liability, ["dividend_due", "payables"]),
        (Income, ["sales"]),
        (IncomeSummaryAccount, ["_profit"]),
        (RetainedEarnings, ["retained_earnings"]),
    ]
