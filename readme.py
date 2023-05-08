# %%
from abacus import Chart, Entry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale", "ppe"],
    expenses=["cogs", "sga", "depreciation_expense"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
    contra_accounts={"ppe": (["depreciation"], "net_ppe")},
)
rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
    "ppe": "Property, plant, equipment",
    "net_ppe": "Property, plant, equipment (net)"
}

entries = [
# pay company capital in cash
Entry(dr="cash", cr="equity", amount=4000),
# acquire storage equipment
Entry(dr="ppe", cr="cash", amount=3000),
# acquire goods
Entry(dr="goods_for_sale", cr="cash", amount=250),
# sell goods worth 180 for 420
Entry(cr="goods_for_sale", dr="cogs", amount=180),
Entry(cr="sales", dr="cash", amount=420),
# pay adminstrative expenses
Entry(cr="cash", dr="sga", amount=50),
# accrue depreciation
Entry(cr="depreciation", dr="depreciation_expense", amount=250),
]

# %%
# create ledger and process entries
ledger = chart.make_ledger().process_entries(entries)


# %%
print(ledger)

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
