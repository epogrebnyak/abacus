# abacus

A minimal, yet valid double-entry accounting system in Python.

## Intended usage

```python
from abacus import Chart, Entry
# See actual code below in README
# chart = ...
# entries = ...
balance_sheet = (chart.make_ledger()
                      .process_entries(entries)
                      .close("retained_earnings")
                      .process_entry(dr="retained_earnings", cr="dividend_payable", amount=700)
                      .balance_sheet()
                      .to_dict())
```

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Try it

Consider an example below. We have an workflow that starts with a chart of accounts
and results in two financial reports - balance sheet and income statement.

1. We start with a chart of accounts of five types: assets, equity, liabilities, income and expenses (there can also be contra accounts).

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

3. Add accounting entries using account names from the chart of accounts.

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

# Close ledger and publsh balance sheet
closed_ledger = ledger.close("re")
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

5. Print balance sheet and income statement to screen with verbose account names and
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

Check out [`readme.py`](readme.py) for a complete code example with
featuring contraccounts (eg depreciation) and dividends.

## Intent

This code is intended as an educational device that informs
users about principles of accounting information systems (AIS).

## Assumptions

Below are some simplifying assumptions made for this code:

1. Account structure is flat, there are no subaccounts.
   This allows to represent ledger as a dictionary, while
   in a real system you will need a tree-like data structure
   to introduce subaccounts.

2. Every entry involves exactly two accounts, there are no compound entries.

3. No cash flow and changes in capital are reported.

4. There are no journals - all records go directly to general ledger.

5. Accounting entry is slim - it has no information other than debit and credit accounts
   and entry amount. Thus we have no extra information for managment accounting or
   detailed tax calculations.

6. Accounts balances can go to negative where they should not and there are little checks for entry validity.

7. XML likely to be a format for accounting reports interchange, while JSON intended for `abacus`.

8. We use just one currency.

9. Closing contra accounts and closing income summary account is stateful and needs careful
   reasoning and implementation. More safeguards can be implemented.

10. Account balances stay on one side, and do not migrate from one side to another.
    Credit accounts have credit balance, debit accounts have debit balance,
    and income summary account is credit account.

## What things are realistic in this code?

1. Entries are stored in a queue and ledger state is calculated
   based on a previous state and a list of entries to be proccessed.

2. The chart of accounts can be fairly complex, up to level of GAAP/IAS compliant.

3. Named entries can code typical transactions.

4. There are contra accounts in chart of accounts.

## Implementation details

1. The code is covered by tests and type annotated.

2. Data structures used are serialisable, so data can be stored and retrieved.

3. We used modern Python features such as subclasssing and pattern matching to make code cleaner.

4. This is experimental software. The upside is that we can make big changes fast. On a downside we do not learn (or earn) from users. We do not compete with SAP, Oralce, Intuit,
   `hledger`, or `gnucash`.

## Feedback

... is much appreciated. I like the idea that compact code for accounting
ledger is possible, but working on it sometimes drains your energy.
Does anyone really need this code? Is this really good code? What useful things
can one do with this code? I like getting feedback and comments,
in [issues](https://github.com/epogrebnyak/abacus/issues)
or otherwise (reddit, Telegram, etc).
