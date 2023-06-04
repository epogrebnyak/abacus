from abacus import Chart

chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    income=["sales"],
    contra_accounts={"sales": ["cashback"]},
)
journal = (
    chart.journal(cash=1200, goods=300, equity=1500)
    .post(dr="ar", cr="sales", amount=440)
    .post(dr="cashback", cr="cash", amount=41)
    .post(dr="cash", cr="ar", amount=250)
    .post(dr="cogs", cr="goods", amount=250)
    .post(dr="sga", cr="cash", amount=59)
    .close()
)
print(journal.balance_sheet())
# BalanceSheet(
#     assets={"cash": 1540, "goods": 50},
#     capital={"equity": 1500, "re": 90},
#     liabilities={},
# )
print(journal.income_statement())
# IncomeStatement(income={"sales": 399},
#                 expenses={"cogs": 250, "sga": 59})
