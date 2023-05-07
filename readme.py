# %%
from abacus import Chart, Entry

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
# close ledger at period end
# (a) move income and expenses to retained earnings
closed_ledger = ledger.close_retained_earnings("re")
# (b) accure dividend and pay out dividend in cash
post_entries = [
    Entry(cr="divp", dr="re", amount=75),
    Entry(dr="divp", cr="cash", amount=75),
]
closed_ledger = closed_ledger.process_entries(post_entries)
# produce balance sheet
balance_sheet = closed_ledger.balance_sheet()

# %%
# print reports
print(income_statement)
print(balance_sheet)
# %%
# Show reports in plain text or rich formatting
from abacus import PlainTextViewer, RichViewer  # noqa: E402

cv2 = PlainTextViewer(rename_dict)
cv2.print(balance_sheet)
cv2.print(income_statement)

cv = RichViewer(rename_dict, width=60)
cv.print(balance_sheet)
cv.print(income_statement)
