# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)

A minimal, yet valid double-entry accounting system provided as `abacus` Python package and `jaba` command line tool.

## Documentation

<https://epogrebnyak.github.io/abacus/>

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

This will install both `abacus` package and `jaba` command line tool:

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Usage

### Step by step code example

1. We start with a chart of accounts of five types: 
   assets, equity, liabilities, income and expenses.
   `abacus` is also aware of contra accounts.

```python

from abacus import Chart, Entry, BalanceSheet, IncomeStatement


chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    liabilities=["dividend_due", "ap"],
    income=["sales"],
    contra_accounts={"sales": ["discounts", "cashback"]},
)
```

2. Next, create a general ledger (book) based on chart of accounts.

```python
book = chart.book()
```

3. Add accounting entries using account names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)  # pay in capital
e2 = Entry(dr="goods", cr="cash", amount=250)    # acquire goods worth 250
e3 = Entry(cr="goods", dr="cogs", amount=200)    # sell goods worth 200
e4 = Entry(cr="sales", dr="cash", amount=400)    # for 400 in cash
e5 = Entry(cr="cash", dr="sga", amount=50)       # administrative expenses
book = book.post_many([e1, e2, e3, e4, e5])
```

4. Close book at accounting period end.

```python
book = book.close()
```

Alternatively you can use chained syntax for steps 2-4 above.

```python
book = (chart.book()
  .post(dr="cash", cr="equity", amount=1000)
  .post(dr="goods", cr="cash", amount=250)
  .post(cr="goods", dr="cogs", amount=200)
  .post(cr="sales", dr="cash", amount=400)
  .post(cr="cash", dr="sga", amount=50)
  .close()
)
```

5. Make income statement.

```python
from abacus import IncomeStatement

income_statement = book.income_statement()
assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 50}
)
```

6. Make balance sheet.

```python
from abacus import BalanceSheet

balance_sheet = book.balance_sheet()
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "ar": 0, "goods": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"dividend_due": 0, "ap": 0}
)
```

7. Print balance sheet and income statement to screen
   with verbose account names and rich formatting.

```python
from abacus import RichViewer


rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "ap": "Accounts payable",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
rv = RichViewer(rename_dict, width=60)
rv.print(balance_sheet)
rv.print(income_statement)
```

8. Use current period end balances to initialize book at the start of next accounting period.

```python
end_balances = book.balances()
next_book = chart.book(starting_balances=end_balances)
assert book.balance_sheet() == next_book.balance_sheet()
```

## Command line

### Create chart of accounts

```bash
jaba chart chart.json touch
jaba chart chart.json set --assets cash ar goods ppe
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba chart chart.json set --liabilities ap dividend_due
jaba chart chart.json set --income sales
jaba chart chart.json set --expenses cogs sga
jaba chart chart.json offset ppe depreciation
jaba chart chart.json offset sales discounts cashback
jaba chart chart.json validate
jaba chart chart.json list
```

### Post entries to ledger and close

```bash
jaba chart chart.json create store.json
jaba store store.json post --dr cash --cr equity --amount 1500
jaba store store.json post goods cash 300
jaba store store.json post cogs goods 250
jaba store store.json post ar sales 440
jaba store store.json post discounts ar 41
jaba store store.json post cash ar 250
jaba store store.json post sga cash 59
jaba store store.json close
jaba store store.json list
```

### Report

```bash
jaba report store.json --balance-sheet
jaba report store.json --income-statement
jaba report store.json --trial-balance
jaba report store.json --account re --assert 90
```

## Feedback

Anything missing in `abacus`? 
Thinking of an applied use case? Used package for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering development of `abacus`.
