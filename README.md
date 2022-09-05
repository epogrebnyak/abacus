# abacus
Learn accounting from Python: T-accounts, ledger and chart of accounts

Check https://github.com/epogrebnyak/abacus/blob/main/abacus/example.py as working example:

1. Specify a system of accounts: 

```python
from abacus import Chart, Entry, Book, make_ledger

chart = Chart(
    assets=["cash", "goods"],
    equity=["equity", "retained_earnings"],
    liabilities=["debt", "payables"],
    income=["sales"],
    expenses=["cogs", "interest"],
)
```

2. Initialise ledger 
```python
L = make_ledger(chart)
```
3. Run transactions:

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
          description="Paid 10% interest."),
    Entry(
        debit="debt", 
        credit="cash", 
        value=40, 
        description="Paid off half of the debt."
    ),
]

for e in entries:
    L.process(e)
```

4. Show the resulting balance sheet:

```python
b = Book(chart, L)
print(b)
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
