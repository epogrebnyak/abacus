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

2. Specify several accounting entries using account names codes from the chart.

```python
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
```

3. From the chart we next create a ledger. It is a dictionary with account names and amounts on debit and credit sides.

With ledger we process entries and the close the accounts at period end
(no dividend).

```python
# open ledger, process entries, make income statement
ledger = chart.make_ledger().process_entries(entries)
income_st = ledger.income_statement()

# close accounts, make balance sheet
closed_ledger = ledger.close("re")
balance_st = closed_ledger.balance_sheet()
```

4. One can see the balance sheet and income statement
   as a data structure and as text for terminal output.

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
