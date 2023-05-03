# abacus

A small, yet valid double-entry accounting system in Python.

Check out [`readme.py`](readme.py) as example:

1. Specify a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)
```

Let us also keep a mapping of longer names for printing:

```python
rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
```

2. Specify several accounting entries using names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000) # pay capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods
e4 = Entry(cr="sales", dr="cash", amount=400)
e5 = Entry(cr="cash", dr="sga", amount=50) # adminstrative expenses
entries = [e1, e2, e3, e4, e5]
```

3. Create a ledger, process entries and close the accounts at period end
   (no dividend no dividend in this case).

```python
# open ledger, process entries
ledger = chart.make_ledger().process_entries(entries)

# make income statement
income_st = ledger.income_statement()

# close accounts
closed_ledger = ledger.close("re")

# make balance sheet
balance_st = closed_ledger.balance_sheet()
```

4. One can see the balance sheet and income statement
   as data structures and as text for terminal output.

```python
print(income_st)
print(balance_st)
```

will show

```
IncomeStatement(income={'sales': 400},
                expenses={'cogs': 200, 'sga': 50})
BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

For text output the following code:

```python
print("Balance sheet", balance_st.as_string(rename_dict), sep="\n")
print("Income statement", income_st.as_string(rename_dict), sep="\n")
```

will return:

```
Balance sheet
Assets            1150  Capital              1150
- Cash            1100  - Equity             1000
- Receivables        0  - Retained earnings   150
- Goods for sale    50  Liabilities             0
                        - Dividend due          0
                        - Payables              0
Income statement
Income                                400
- Sales                               400
Expenses                              250
- Cost of goods sold                  200
- Selling, general and adm. expenses   50
Net profit                            150
```
