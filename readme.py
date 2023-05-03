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
income_st = ledger.income_statement()
closed_ledger = ledger.close("re")
balance_st = closed_ledger.balance_sheet()

print(income_st)
# IncomeStatement(income={'sales': 400},
#                 expenses={'cogs': 200, 'sga': 50})

print(balance_st)
# BalanceSheet(
#    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
#    capital={"equity": 1000, "re": 150},
#    liabilities={"divp": 0, "payables": 0}
# )

from abacus import ConsoleViewer

cv = ConsoleViewer(rename_dict, width=60)
cv.print(balance_st)
cv.print(income_st)

# %%
"""
                       Balance sheet                        
 Assets                 1150  Capital                  1150 
   Cash                 1100    Equity                 1000 
   Receivables             0    Retained earnings       150 
   Goods for sale         50  Liabilities                 0 
                                Dividend due              0 
                                Payables                  0 
 Total                  1150  Total                    1150 
                      Income statement                      
 Income                                                 400 
   Sales                                                400 
 Expenses                                               250 
   Cost of goods sold                                   200 
   Selling, general and adm. expenses                    50 
 Profit                                                 150
"""
