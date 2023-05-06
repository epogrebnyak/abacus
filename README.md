# abacus

A minimal, yet valid double-entry accounting system in Python.

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Accounting equations

[Expanded accounting equation][eq] `(1)` is a good reference for an accounting system,
as mentioned by [@mafm, author of ledger.py](https://github.com/mafm/ledger.py/blob/master/doc/Ledger.md#debits-and-credits-etc)[^1]:

[^1]: Some students indicate expanded accounting equation [makes learning a bit smoother](https://www.reddit.com/r/Accounting/comments/137e3lz/i_plan_on_pursuing_a_bachelors_in_accounting_soon/jitcu6g/?context=3).

```
Assets + Expenses = Capital + Liabilites + Income   (1)
```

Expanded accounting equation is slightly less advertised than its reduced form, [an accounting identity](https://en.wikipedia.org/wiki/Accounting_identity)
`(2)`, which is valid at accounting period end:

[eq]: https://www.accaglobal.com/gb/en/student/exam-support-resources/foundation-level-study-resources/fa1/technical-articles/accounting-equation.html

```
Assets = Capital + Liabilites                      (2)
```

Also note that profit [follows][^2]:

```
Profit = Income - Expenses                        (3)
```

[^2] [The profit earned by the business increases capital](https://www.open.edu/openlearn/mod/oucontent/view.php?id=31735&printable=1).

In short an accounting system:

- keeps track of the equation `(1)` within the accounting period, and
- produces equations `(2)` and `(3)` at accounting period end.

## Try it

Consider an example below that demonstrates accounting workflow.

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
e5 = Entry(cr="cash", dr="sga", amount=50)             # administrative expenses
ledger = ledger.process_entries([e1, e2, e3, e4, e5])
```

4. Close accounts at period end, produce income statement and balance sheet.

```python
# Create income statement
income_statement = ledger.income_statement()
print(income_statement)

# Close accounts
closed_ledger = ledger.close(
    retained_earnings_account_name="re",
    closing_entries=[ClosingEntry(cr="divp", dr="re", amount=75)]
)

# Publish balance sheet
balance_sheet = closed_ledger.balance_sheet()
print(balance_sheet)
```

```python
IncomeStatement(income={'sales': 400}, expenses={'cogs': 200, 'sga': 50})
```

```python
BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

5. Balance sheet and income statement can be printed to screen with verbose account names and
   rich formatting.

```python
from abacus import RichViewer

rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
cv = RichViewer(rename_dict, width=60)
cv.print(balance_sheet)
cv.print(income_statement)
```

Check out [`readme.py`](readme.py) for a complete code example.

## Simplifications

This code is intended as an educational device that informs
users about principles of accounting information systems (AIS).

Below are some simplifications made for this code:

1. Account structure is flat, there are no subaccounts.
   This allows to represent ledger as a dictionary, while
   in a real system you will need a tree-like data structure
   to represent subaccounts.

2. No contraccounts (eg depreciation) and accumulation (netting) rules
   for contraccounts introduced yet.

3. Every entry involves exactly two accounts, there are no compound entries.

4. No cash flow and changes in capital are reported.

5. There are no journals - all records go directly to general ledger.

6. Accounting entry is slim - it has no information other than debit and credit accounts
   and entry amount.

7. Accounts balances can go to negative, where they should not and there are practically no checks for entry validity.

8. Thus this system has no information for managment accounting or tax calculations.

9. XML likely to be a format for accounting data interchange (JSON intended for `abacus`).

10. AIS should work on business event level, and know to translate business event
    to accoutnign transactions and transactions to entries. We work just on entries level.

11. We use just one currency.

What things are realistic it this code?

1. Entries are stored in a queue and ledger state is calculated
   based on a previous state and a list of entries to be proccessed.

2. The chart of accounts can be fairly complex.

3. Named entries indicate typical accounting transactions.

4. Contra accounts is progress.

Implementation detail:

1. The code is covered by tests and type annotated.

2. Data structures used are serialisable, data can be stored and retrieved.

3. Using better Python features (eg subclasssing, pattern matching) for cleaner, understandable code.

4. There is no production load - this is experimental software. Good side: can make big changes fast. Other side: we do not learn (or earn) from users.
