from abacus import Chart

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
