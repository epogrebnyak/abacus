from abacus import Chart
from abacus.accounts import (
    Asset,
    Capital,
    RetainedEarnings,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
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


def test_chart_flat():
    assert chart.set_retained_earnings_account("retained_earnings").flat() == [
        (Asset, ["cash", "receivables", "goods_for_sale", "ppe"]),
        (Expense, ["cogs", "sga", "depreciation_expense"]),
        (Capital, ["equity", "retained_earnings"]),
        (Liability, ["dividend_due", "payables"]),
        (Income, ["sales"]),
        (IncomeSummaryAccount, ["_profit"]),
        (RetainedEarnings, ["retained_earnings"]),
    ]

print(chart.set_retained_earnings_account("retained_earnings").flat())