# abacus

A small, yet valid double-entry accounting system in Python.
(Can accounting be a DSL? Why not?)

Check out [`readme.py`](readme.py) as example:

1. Specify a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
from abacus import Book, Chart, BalanceSheet, RawEntry

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["payables"],
    income=["sales"],
)
```

2. Specify accounting entry using account codes from the chart.

```python
e1 = RawEntry(dr="cash", cr="equity", amount=1000)
e2 = RawEntry(dr="goods_for_sale", cr="cash", amount=250)

book.append_raw_entry(e1)
book.append_raw_entry(e2)
```

3. After entries are added, let's see the general ledger.
   It is a dictionary with account names and debit/credit side records.

```python
print(book.get_ledger())

{
    "cash": DebitAccount(debits=[1000], credits=[250]),
    "receivables": DebitAccount(debits=[], credits=[]),
    "goods_for_sale": DebitAccount(debits=[250], credits=[]),
    "cogs": DebitAccount(debits=[], credits=[]),
    "sga": DebitAccount(debits=[], credits=[]),
    "equity": CreditAccount(debits=[], credits=[1000]),
    "payables": CreditAccount(debits=[], credits=[]),
    "sales": CreditAccount(debits=[], credits=[]),
}
```

4. One can also see the interim balance sheet:

```python
print(book.get_balance_sheet())

BalanceSheet(
    assets={"cash": 750, "receivables": 0, "goods_for_sale": 250},
    capital={"equity": 1000, "current_profit": 0},
    liabilities={"payables": 0},
)
```

5. For ease of use we can give disticitve names to entries.
   For example, `invoice_buyer=("receivables", "sales")` means
   that we can use named entry `("invoice_buyer", 250)` instead of
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

6. Write more accounting entries using names defined above.

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

7. Append all entries to ledger and get a balance sheet.

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
