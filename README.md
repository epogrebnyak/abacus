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

## Minimal example

A freshly created trading Klondike Trading Company (KTC) have recorded the following transactions.

|     | Transaction Title                            |        Debit        |       Credit        | Amount |
| --- | -------------------------------------------- | :-----------------: | :-----------------: | -----: |
| 1   | Shareholders paid up capital contribution    |        Cash         |       Equity        |   1000 |
| 2   | Purchased goods for resale                   |      Inventory      |        Cash         |    800 |
| 3   | Invoiced client on contract #2023-001        | Accounts Receivable |       Revenue       |    965 |
| 4   | Provided discount on contract #2023-001      |      Discounts      | Accounts Receivable |     30 |
| 5   | Recorded cost of sales on contract #2023-001 |        COGS         |      Inventory      |    600 |
| 6   | Paid salary to contract manager              |    SG&A Expenses    |        Cash         |    185 |
| 7   | Accepted payment on contract #2023-001       | Accounts Receivable |        Cash         |    725 |
| 8   | Accrued dividend after announcement          |  Retained Earnings  |    Dividend Due     |     60 |

Using `abacus` you can define a chart of accounts for KTC, create a general ledger, post
entries and produce balance sheet and income statement at accounting period end.

### 1. Chart

Define a chart of accounts of five types (assets, equity, liabilities, income and expenses),
specify retained earnings account name and optionally add contra accounts.

```python
from abacus import Chart

chart = (Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["dividend_due"],
    income=["sales"])
  .set_retained_earnings("re")
  .offset("sales", ["discounts"])
)
```

### 2. Ledger

Create a general ledger based on the chart of accounts,
post entries and close accounts at accounting period end.

```python
book = (chart.book()
  .post(dr="cash", cr="equity", amount=1000)
  .post(dr="goods", cr="cash", amount=800)
  .post(dr="ar", cr="sales", amount=965)
  .post(dr="discounts", cr="ar", amount=30)
  .post(dr="cogs", cr="goods", amount=600)
  .post(dr="sga", cr="cash", amount=185)
  .post(dr="cash", cr="ar", amount=725)
  .close()
  .after_close(dr="re", cr="dividend_due", amount=60)
)
```

### 3. Reports

Make trail balance, income statement and balance sheet and print them to screen
with verbose account names and rich or regular formatting.

```python
from abacus import RichViewer, PlainTextViewer

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}

tv = PlainTextViewer(rename_dict)
tv.print(balance_sheet)
tv.print(income_statement)

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

print(income_statement)
assert income_statement == IncomeStatement(
    income={'sales': 935},
    expenses={'cogs': 600, 'sga': 185}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
    assets={"cash": 740, "ar": 210, "goods": 200},
    capital={"equity": 1000, "re": 90},
    liabilities={"dividend_due": 60}
)
```

### End balances

You can use end balances from current period to initialize ledger at the start of next accounting period.

```python
end_balances = book.nonzero_balances()
print(end_balances)
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
bx chart set --liabilities dividend_due
bx chart set --income sales
bx chart set --expenses cogs sga
bx chart offset sales --contra-accounts discounts
bx chart list
```

### Post entries to ledger and close

```bash
bx ledger start
bx ledger post --debit cash --credit equity --amount 1000
bx ledger post --debit goods --credit cash --amount 800
bx ledger post --debit ar --credit sales --amount 965
bx ledger post --debit discounts --credit ar --amount 30
bx ledger post --debit cogs --credit goods --amount 600
bx ledger post --debit sga --credit cash --amount 185
bx ledger post --debit cash --credit ar --amount 725
bx ledger close
bx ledger post --debit re --credit dividend_due --amount 60 --after-close
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
bx show account sales
```

`assert` command will make the program complain
if account balance is not equal to provided value.
This is useful for testing.

```bash
bx assert cash 740
```

## Feedback

Anything missing in `abacus`?
Got a good use case for `abacus` or used `abacus` for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering development of `abacus`.
