# %%
from abacus import Chart, Entry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale", "ppe"],
    expenses=["cogs", "sga", "dexp"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
    contra_accounts={
        "ppe": (["depr"], "net_ppe"),
        "sales": (["discount", "returns"], "net_sales"),
    },
).set_retained_earnings_account("re")

rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
    "dexp": "Depreciation expense",
    "depr": "Accumulated depreciation",
    "ppe": "Property, plant, equipment",
    "net_ppe": "Property, plant, equipment (net)",
    "net_sales": "Sales (net)",
}

entries = [
    # pay company capital in cash
    Entry(dr="cash", cr="equity", amount=4000),
    # acquire property for storage
    Entry(dr="ppe", cr="cash", amount=3000),
    # acquire goods for resale
    Entry(dr="goods_for_sale", cr="cash", amount=250),
    # sell goods worth 180 for 620 with discounts of 45 and 25
    Entry(cr="goods_for_sale", dr="cogs", amount=180),
    Entry(cr="sales", dr="receivables", amount=620),
    Entry(dr="cash", cr="receivables", amount=500),
    Entry(cr="cash", dr="discount", amount=25),
    Entry(cr="payables", dr="discount", amount=45),
    # pay adminstrative expenses
    Entry(cr="cash", dr="sga", amount=50),
    # accrue depreciation
    Entry(cr="depr", dr="dexp", amount=250),
]

# %%
# create ledger and process entries
ledger = chart.make_ledger().process_entries(entries)

# %%
# create income statement
income_statement = ledger.income_statement()
print(income_statement)
print(income_statement.current_profit())

# %%
# close ledger at period end
# (a) move income and expenses to retained earnings
closed_ledger = ledger.close()
# (b) accure dividend
post_entries = [
    Entry(cr="divp", dr="re", amount=45),
]
closed_ledger = closed_ledger.process_entries(post_entries)
# produce balance sheet
balance_sheet = closed_ledger.balance_sheet()
print(balance_sheet)

# %%
# Show reports in plain text or rich formatting
from abacus import PlainTextViewer, RichViewer  # noqa: E402

tv = PlainTextViewer(rename_dict)
tv.print(balance_sheet)
tv.print(income_statement)

rv = RichViewer(rename_dict, width=60)
rv.print(balance_sheet)
rv.print(income_statement)
