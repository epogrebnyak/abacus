# %%
from abacus import Chart, Entry, ClosingEntry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)
rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}

# pay company capital in cash
e1 = Entry(dr="cash", cr="equity", amount=1000)
# acquire goods
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
# sell goods worth 200 for 400
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
e4 = Entry(cr="sales", dr="cash", amount=400)
# adminstrative expenses
e5 = Entry(cr="cash", dr="sga", amount=50)
entries = [e1, e2, e3, e4, e5]

# %%
# create ledger and process entries
ledger = chart.make_ledger().process_entries(entries)

# %%
# create income statement
income_statement = ledger.income_statement()

# %%
# close ledger at period end and accrure dividend
closed_ledger = ledger.close(
    "re", closing_entries=[ClosingEntry(cr="divp", dr="re", amount=75)]
)
balance_sheet = closed_ledger.balance_sheet()

# %%
# print reports
print(income_statement)
print(balance_sheet)
# %%
# Show reports in color
from abacus import ConsoleViewer

cv = ConsoleViewer(rename_dict, width=60)
cv.print(balance_sheet)
cv.print(income_statement)
