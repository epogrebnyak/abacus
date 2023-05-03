# %%
from abacus import Chart, Entry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)

# pay capital
e1 = Entry(dr="cash", cr="equity", amount=1000)
# acquire goods
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
# sell goods
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
e4 = Entry(cr="sales", dr="cash", amount=400)
# adminstrative expenses
e5 = Entry(cr="cash", dr="sga", amount=50)
entries = [e1, e2, e3, e4, e5]

ledger = chart.make_ledger().process_entries(entries)
print(ledger.income_statement())
# IncomeStatement(income={'sales': 400},
#                 expenses={'cogs': 200, 'sga': 50})

ledger = ledger.close("re")
print(ledger.balance_sheet())
# BalanceSheet(
#    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
#    capital={"equity": 1000, "re": 150},
#    liabilities={"divp": 0, "payables": 0},
# )
