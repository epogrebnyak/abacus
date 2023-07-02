# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)

A minimal, yet valid double-entry accounting system, provided as a Python package and a command line tool.

## Documentation

<https://epogrebnyak.github.io/abacus/>

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

This will install both `abacus` package and the `bx` command line tool.

## Usage

There are three steps in using `abacus`:

1. create a chart of accounts,
2. create general ledger and post entries,
3. make trial balance, balance sheet and income statement reports.

### 1. Chart

Define a chart of accounts of five types (assets, equity, liabilities, income and expenses),
specify retained earnings account name and add contra accounts if you need to use them.

```python
from abacus import Chart

chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["dividend_due", "ap"],
    income=["sales"],
)
chart.set_retained_earnings("re")
chart.offset("sales", ["discounts", "refunds"])
```

### 2. Ledger

Create a general ledger based on the chart of accounts,
post entries and close accounts at accounting period end.

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

### 3. Reports

Make trail balance, income statement and balance sheet and print them to screen
with verbose account names and rich or regular formatting.

```python
from abacus import RichViewer

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "ap": "Accounts payable",
    "ppe": "Fixed assets",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
rv = RichViewer(rename_dict, width=80)
rv.print(balance_sheet)
rv.print(income_statement)
```

The result should look like screenshot below.

![](https://user-images.githubusercontent.com/9265326/249445794-7def0fc2-934b-49fa-a3ad-9137072a2900.png)

<details>
<summary> Details about correctness checks and end balances.
</summary>

### Check values

As a reminder `assert` statement in Python will raise exception if provided wrong comparison.
These checks will execute and this way we will know the code in README is up to date and correct.

```python
from abacus import IncomeStatement, BalanceSheet

assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 50}
)
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "ar": 0, "goods": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"dividend_due": 0, "ap": 0}
)
```

### End balances

You can use end balances from current period to initialize ledger at the start of next accounting period.

```python
end_balances = book.nonzero_balances()
assert end_balances  == {'cash': 1100, 'goods': 50, 'equity': 1000, 're': 150}
next_book = chart.book(starting_balances=end_balances)
```

</details>

## Command line

Similar operations with chart, ledger and reports can be performed on the command line.

### Create chart of accounts

```bash
bx init --force
bx chart set --assets cash ar goods
bx chart set --equity equity
bx chart set --retained-earnings re
bx chart set --liabilities ap
bx chart set --income sales
bx chart set --expenses cogs sga
bx chart offset sales --contra-accounts discounts cashback
bx chart list
```

### Post entries to ledger and close

```bash
bx ledger start
bx ledger post cash equity 1000
bx ledger post goods cash 300
bx ledger post cogs goods 250
bx ledger post ar sales 440
bx ledger post discounts ar 41
bx ledger post cash ar 150
bx ledger post sga cash 69
bx ledger close
bx ledger list --business
bx ledger list --close
```

### Report

```bash
bx show report --balance-sheet
bx show report --income-statement
bx show balances
```

You can save end balances to a file to initialize next period ledger.

```bash
bx show balances --json > end_balances.json
```

### Account information

```bash
bx show account cash
bx show account ar
bx show account goods
bx show account equity
bx show account re
```

`assert` command will make the program complain
if account balance is not equal to provided value.
This is useful for testing.

```bash
bx assert cash 781
bx assert ar 249
bx assert goods 50
bx assert equity 1000
bx assert re 80
```

## Feedback

Anything missing in `abacus`?
Got a good use case for `abacus` or used `abacus` for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering development of `abacus`.
