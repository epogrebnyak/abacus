# abacus

A small, yet valid double-entry accounting system in Python.
(Can accounting be a DSL? Why not?) 

Check out [`readme.py`](readme.py) as example:

1. Specify a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
from abacus import Book, Chart, BalanceSheet

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "retained_earnings"],
    liabilities=["payables"],
    income=["sales"],
)
```

2. For ease of use give disticitve names to entries. For example,
`invoice_buyer=("receivables", "sales")` means that we can use 
named entry `("invoice_buyer", 250)` instead of 
`RawEntry(dr="receivables", cr="sales", amount=250)`.

```python
named_entry_shortcodes = dict(
    pay_shareholder_capital=("cash", "equity"),
    buy_goods_for_cash=("goods_for_sale", "cash"),
    invoice_buyer=("receivables", "sales"),
    transfer_goods_sold=("cogs", "goods_for_sale"),
    accept_payment=("cash", "receivables"),
    accrue_salary=("sga", "payables"),
    pay_salary=("payables", "cash"),
)
```
3. Write some accounting entries using names defined above. 

```python
named_entries = [
    # start a company
    ("pay_shareholder_capital", 501),
    ("pay_shareholder_capital", 499),
    # acquire goods
    ("buy_goods_for_cash", 820),
    # one order
    ("invoice_buyer", 600),
    ("transfer_goods_sold", 360),
    ("accept_payment", 549),
    # pay labor
    ("accrue_salary", 400),
    ("pay_salary", 345),
    # another order
    ("invoice_buyer", 160),
    ("transfer_goods_sold", 80),
    ("accept_payment", 80),
]
```

4. Let's create a ledger, append all entries and get a balance sheet.

```python
book = Book(chart, named_entry_shortcodes)
book.append_named_entries(named_entries)
balance_sheet = book.get_balance_sheet()
```
The resulting balance sheet looks like this:

```python
BalanceSheet(
    assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
    capital={"equity": 1000, "retained_earnings": 0, "current_profit": -80},
    liabilities={"payables": 55}
)
```