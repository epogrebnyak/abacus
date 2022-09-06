# abacus

Learn accounting from by programming a small accounting system Python.

Check out [`readme.py`](readme.py) as example:

1. Specify a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
from abacus import Chart, Entry, Book, make_ledger, make_balance_sheet

chart = Chart(
    assets=["cash", "goods"],
    equity=["equity", "retained_earnings"],
    liabilities=["debt", "payables"],
    income=["sales"],
    expenses=["cogs", "interest"],
)
```

2. Initialise [ledger](https://en.wikipedia.org/wiki/Ledger). The ledger will hold transactions 
that we add on the next step.

```python
ledger = make_ledger(chart)
```
3. Add transactions:

```python
entries = [
    Entry(
        debit="cash",
        credit="equity",
        value=20,
        description="Shareholders paid in capital in cash.",
    ),
    Entry(debit="cash", 
          credit="debt", 
          value=80, 
          description="Firm got a loan."),
    Entry(
        debit="goods",
        credit="cash",
        value=50,
        description="Bought some goods for resale.",
    ),
    Entry(
        debit="cash",
        credit="sales",
        value=75,
        description="Sold goods worth 40 for 75, got more cash.",
    ),
    Entry(
        debit="cogs",
        credit="goods",
        value=40,
        description="Accounted expenses for goods sold.",
    ),
    Entry(debit="interest", 
          credit="cash", 
          value=8, 
          description="Paid 10 percent interest."),
    Entry(
        debit="debt", 
        credit="cash", 
        value=40, 
        description="Paid off half of the debt."
    ),
]

for e in entries:
    ledger.process(e)
```

4. Show the resulting balance sheet:

```python
balance_sheet = make_balance_sheet(chart, ledger)
print(balance_sheet)
```

```
Assets         Capital
  Cash.... 77    Equity.............. 20
  Goods... 10    Retained earnings...  0
                 Profit.............. 27
               Liabilities
                 Debt................ 40
                 Payables............  0
```
