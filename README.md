# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)

A minimal, yet valid double-entry accounting system written in Python:
- `abacus` package, 
- `jaba` command line tool (_J_SON `_aba_cus`).


## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Minimal example

```python
from abacus import Chart, BalanceSheet, IncomeStatement

chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    income=["sales"],
    contra_accounts={"sales": ["cashback"]},
)
journal = (
    chart.journal(cash=1200, goods=300, equity=1500)
    .post(dr="ar", cr="sales", amount=440)
    .post(dr="cashback", cr="cash", amount=41)
    .post(dr="cash", cr="ar", amount=250)
    .post(dr="cogs", cr="goods", amount=250)
    .post(dr="sga", cr="cash", amount=59)
    .close()
)
print(journal.balance_sheet())
# BalanceSheet(assets={'cash': 1350, 'ar': 190, 'goods': 50},
#              capital={'equity': 1500, 're': 90},
#              liabilities={})
print(journal.income_statement())
# IncomeStatement(income={'sales': 399},
#                 expenses={'cogs': 250, 'sga': 59})
```

## What `abacus` is for?

`abacus` aims to complete an accounting cycle in following steps.

1. Define a chart of accounts with five types of accounts (assets, expenses, capital, liabilities and income) and contra accounts (eg depreciation).
2. Create a blank general ledger for a new company or a general ledger with starting balances from previous period for existing company.
3. Post entries to a general ledger individually or in bulk.
4. View trial balance.
5. Make adjustment entries.
6. Close income and expenses accounts and transfer current period profit (loss) to retained earnings.
7. Make post-close entries (eg accrue dividend due to shareholders upon dividend announcement).
8. View and save income statement and balance sheet reports.
9. Save period end account balances and use them to initialize a general ledger at the start of a next accounting period.

More usage ideas in [Motivation](#motivation) section below.

## Upcoming in 0.5.0 - command line interface (CLI)

See [milestone](https://github.com/epogrebnyak/abacus/issues?q=is%3Aopen+is%3Aissue+milestone%3A%220.5.0+release%3A+CLI+with+json+file+backend%22).

## Step by step example

1. We start with a chart of accounts of five types: assets, equity, liabilities, income and expenses.

```python
from abacus import Chart, Entry


chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    liabilities=["divp", "payables"],
    income=["sales"],
)
```

2. Next, create a general ledger based on chart of accounts.

```python
journal = chart.journal()
```

3. Add accounting entries using account names from the chart of accounts
   and close ledger at period end.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)        # pay in capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods worth 250
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods worth 200
e4 = Entry(cr="sales", dr="cash", amount=400)          # for 400 in cash
e5 = Entry(cr="cash", dr="sga", amount=50)             # administrative expenses
journal = journal.post_many([e1, e2, e3, e4, e5]).close()
```

4. Make income statement.

```python
from abacus import IncomeStatement

income_statement = journal.income_statement()
assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 50}
)
```

5. Make balance sheet.

```python
from abacus import BalanceSheet

balance_sheet = journal.balance_sheet()
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

6. Print balance sheet and income statement to screen
   with verbose account names and rich formatting.

```python
from abacus import RichViewer


rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
rv = RichViewer(rename_dict, width=60)
rv.print(balance_sheet)
rv.print(income_statement)
```

## Motivation

### Original intent

`abacus` started as a project to demonstrate principles of double-entry accounting
through Python code, in spirit of [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x).
You can use `abacus` to teach basics of accounting and accounting information systems (AIS).

### Other uses

- Use as a software component with other open source tools (such as fast `medici` ledger).
- Convert reports between charts of accounts (eg local accounting standards to IFRS).
- Process streams of business events in business simulations.
- Generate prompts and enhance a large language model with structured outputs in accounting.

## Assumptions

Below are some simplifying assumptions and behaviors made for this code.
Some assumptions may be relaxed, some will remain a feature.

1. Account structure is flat, there are no subaccounts. To override one can use `cash:petty` and `cash:bank_account` to mimic subaccounts.

2. Every entry involves exactly two accounts, there are no compound entries.

3. No cash flow and changes in capital are reported.

4. There are no journals - all records go directly to general ledger.

5. Accounting entry is slim and has no information other than debit and credit accounts
   and entry amount. In future may add title, timestamp, hash and meta information.

6. Accounts balances can go to negative where they should not and there are no checks for entry validity.

7. We use [just one currency](https://www.mscs.dal.ca/~selinger/accounting/).

8. Account balances stay on one side, and do not migrate from one side to another.
   Credit accounts have credit balance, debit accounts have debit balance,
   and income summary account is a credit account.

9. Money amounts are integers, will change to `Decimal`.

10. Renamed accounts are dropped from the ledger. When `sales` becomes `net_sales`
    after a contra accounts like `discounts` are netted, `sales` leave the ledger,
    and `net_sales` remains.

## What things are realistic in this code?

1. Entries are stored in a queue and ledger state is calculated
   based on a previous state and a list of entries to be processed.

2. The chart of accounts can be fairly complex.

3. Chart of accounts may include contra accounts. Temporary contra accounts
   for income (eg discounts given) and expense (eg discounts or cashbacks received)
   are cleared at period end, permanent contra accounts
   (eg accumulated depreciation) are carried forward.

4. You can give a name to typical dr/cr account pairs and use this name to record transactions.

5. Accounts can be renamed for reporting purposes, thus opening a way to internationalisation.
   You can keep a short name like `cash` or account code in ledger and rename `cash` to `नकद` for a report.

## Implementation details

1. The code is covered by tests, linted and type annotated.

2. Data structures used are serialisable, so inputs and outputs can be stored and retrieved.

3. XML likely to be a format for accounting reports interchange, while JSON and YAML are intended for `abacus`.

4. Modern Python features such as subclasssing and pattern matching help to make code cleaner.
   Classes like `Asset`, `Expense`, `Capital`, `Liability`, `Income` pass forward useful information about account types and their behaviors.

5. This is experimental software. The upside is that we can make big changes fast. On a downside we do not learn (or earn) from users, at least yet.

6. `abacus` is not optimised for performance and likely to be slow under high load.

## Similar projects

JavaScript:

- [medici](https://github.com/flash-oss/medici) (JavaScript) is a ledger store optimized for high loads (does not enforce any chart of accounts conventions).

Python:

- [pyluca](https://github.com/datasignstech/pyluca) is actively developed and has practical use in mind, coined a term 'headless ledger' (different interface and data structures than `abacus`).
- [ledger.py](https://github.com/mafm/ledger.py) started about 10 years ago with Python 2, once a [hledger](https://hledger.org/) competitor, has good documentation, but last commit in 2018.

Plain text accounting:

- `Ledger`, `hledger` and `beancount` are leaders in [plain text accounting](https://plaintextaccounting.org/#tools)
- See also [gnucash](https://www.gnucash.org/)

More:

- Open source ERPs (Odoo, ERPNext) also have accounting functionality.
- [`double-entry-accounting`](https://github.com/topics/double-entry-accounting) tag on Github

## Feedback

Anything missing in `abacus`? Noticed a flaw in accounting logic or a lousy variable name?
Got a use case for `abacus`? Used package in classroom for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering development of `abacus`.
