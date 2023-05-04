# abacus

A small, yet valid double-entry accounting system in Python.

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

## Install 

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Try it

Consider an example below that demonstrates key parts of the accounting workflow.

1. We start with a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
from abacus import Chart, Entry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)
```

2. Next, create a general ledger based on chart of accounts.

```python
ledger = chart.make_ledger()
```

3. Add accounting entries using the account names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)        # pay capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods
e4 = Entry(cr="sales", dr="cash", amount=400)
e5 = Entry(cr="cash", dr="sga", amount=50)             # adminstrative expenses
ledger = ledger.process_entries([e1, e2, e3, e4, e5])
```

4. Close accounts at period end, produce income statement and balance sheet.

```python
# Create income statement
income_statement = ledger.income_statement()
print(income_statement)

# Close accounts at period end and create balance sheet
closed_ledger = ledger.close(retained_earnings_account_name="re")
balance_sheet = closed_ledger.balance_sheet()
print(balance_sheet)
```

```python
IncomeStatement(income={'sales': 400}, expenses={'cogs': 200, 'sga': 50})
BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

5. Balance sheet and income statement can be printed 
   to screen with more verbose account names and formatting
   (prints with color in console).

```python
from abacus import ConsoleViewer

rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
cv = ConsoleViewer(rename_dict, width=60)
cv.print(balance_sheet)
cv.print(income_statement)
```

```console
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
```

Check out [`readme.py`](readme.py) for a complete code example.


## Simplifications

This code is intended as an educational device that informs
users about principles of accounting information systems (AIS).

Below are some simplifications made for this code:

1. Account structure is flat, there are no subaccounts.
   (This allows to represent ledger as a dictionary, while 
   in a real system you will need a tree data structure).

2. No contraccounts (eg depreciation) and accumulation (netting) rules
   for contraccounts.

3. Every entry involves exactly two accounts, there are no multiple entries. 

4. No cash flow and changes in capital reports.

5. There are no dividends in examples.

6. No journals - all records go directly to general ledger.

7. Accounting entry has no information other than dr and cr accounts 
   and amount. 

8. Accounts balances can go to negative, little checks for entry validity. 

9. Practically no information for managment accounting or tax calculations.

10. XML likely to be a format for accounting data interchange.

What things are realistic though?

1. Entries are stored in a queue and ledger state is calculated 
   based on a previous state and a list of entries to be proccessed.

2. The chart of accounts can be fairly complex.

3. Named entries indicate typical accounting transactions. 

Implementation:

1. The code is covered by tests and type annotated.

2. Data structures used are serialisable, data can be stored and retrieved.

3. Using better Python features (eg subclasssing, etc) for cleaner, understandable code.
