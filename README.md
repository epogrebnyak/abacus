# abacus

A small, yet valid double-entry accounting system in Python.

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

Consider the following four steps as a demonstration example.

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

4. Add accounting entries using the account names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)        # pay capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods
e4 = Entry(cr="sales", dr="cash", amount=400)
e5 = Entry(cr="cash", dr="sga", amount=50)             # adminstrative expenses
ledger = ledger.process_entries([e1, e2, e3, e4, e5])
```

3. Close accounts at period end and produce income statement and balance
   sheet.

```python
# Create income statement
income_statement = ledger.income_statement()
print(income_statement)
```

```python
IncomeStatement(income={'sales': 400},
                expenses={'cogs': 200, 'sga': 50})
```

````python
# Close accounts at period end and create balance sheet
closed_ledger = ledger.close(retained_earnings_account_name="re")
balance_sheet = closed_ledger.balance_sheet()
print(balance_sheet)

```python
BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
````

4. We can also print balance sheet and income statement as text
   using longer account names.

```python
rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
print("Balance sheet", balance_st.as_string(rename_dict), sep="\n")
print("Income statement", income_st.as_string(rename_dict), sep="\n")
```

```console
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

Check out [`readme.py`](readme.py) for complete code example.
