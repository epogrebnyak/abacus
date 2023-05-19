# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)

A minimal, yet valid double-entry accounting system in Python that works with user-defined chart of accounts,
provides a general ledger and can close accounts properly at period end.
`abacus` produces trial balance, income statement and balance sheet reports.

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Next release: 0.3.0 Pipelines

A pipeline will allow to create lists of entries using commands
to close contra accounts as well as closing temporary ("nominal") accounts
(income, expense and income summary accounts) and will add current period
profit to retained earnings.

A pipeline will contain a start ledger (possibly empty ledger made from a chart of accounts), a list of postings to a ledger and methods to grow this list like
`add_entries()`, `.close_income()` or `.close_expenses()`.
These closing methods will add new postings to a list of postings, but creating a new ledger is postponed until all required entries are added to the list.

This enables composability of a pipeline, even though at a cost: a pipeline may need to execute internally to produce next ledger state. For example, to close income or expense accounts one must execute all postings to these accounts and find out the balance of this account.

The `run()` method will execute a pipeline py posting all entries to a start ledger. Pipeines should help to produce ledger states required for the income statement and balance sheet or other points in time of the accounting cylce.

Pipeines can be further optimised for performance, the initial implementation
disregards speed and computational intensity of a pipeline.

Affected issues are [#11](https://github.com/epogrebnyak/abacus/issues/11), [#10](https://github.com/epogrebnyak/abacus/issues/10) and [#7](https://github.com/epogrebnyak/abacus/issues/7).

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## Minimal working example

```python
from abacus import Chart, Entry, BalanceSheet


chart = Chart(
    assets=["cash"],
    expenses=["overhead"],
    equity=["equity", "retained_earnings"],
    liabilities=["dividend_payable"],
    income=["sales"],
    contra_accounts={"sales": (["discounts"], "net_sales")},
)
entries = [
    Entry("cash", "equity", 500),   # started a company...
    Entry("cash", "sales", 150),    # selling thin air (zero cost of sales)
    Entry("discounts", "cash", 30), # with a discount
    Entry("overhead", "cash", 50),  # and overhead expense
]
balance_sheet = (
    chart.make_ledger()
    .process_entries(entries)
    .close("retained_earnings")
    .process_entry(dr="retained_earnings", cr="dividend_payable", amount=35)
    .balance_sheet()
)
# check what we've got
assert balance_sheet == BalanceSheet(
    assets={"cash": 570},
    capital={"equity": 500, "retained_earnings": 35},
    liabilities={"dividend_payable": 35},
)
```

## Step by step example

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

3. Add accounting entries using account names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)        # pay in capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods worth 250
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods worth 200
e4 = Entry(cr="sales", dr="cash", amount=400)          # for 400 in cash
e5 = Entry(cr="cash", dr="sga", amount=50)             # administrative expenses
ledger = ledger.process_entries([e1, e2, e3, e4, e5])
```

4. Make income statement at accounting period end.

```python
from abacus import IncomeStatement

income_statement = ledger.income_statement()
print(income_statement)
assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 50}
)
```

5. Close ledger and make balance sheet.

```python
from abacus import BalanceSheet

closed_ledger = ledger.close("re")
balance_sheet = closed_ledger.balance_sheet()
print(balance_sheet)


assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

6. Print balance sheet and income statement to screen with verbose account names and
   rich formatting.

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

Check out [`readme.py`](readme.py) for a complete code example
with several contraccounts (depreciation, discounts) and dividend payout.

## Intent

`abacus` started as an educational device to inform users about principles of double-entry accounting
and accounting information systems (AIS) through a simple Python program,
in spirit of [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) projects.

Usage ideas:

- Teach accounting or AIS with it.
- Build a `streamlit` app as a ledger demo.
- Use with other accounting software as a component.
- Build business simulations (e.g. generate a stream of business events and make operational, financing and investment decisions based on financial reports)
- Enhance a large language model with structured outputs in accounting.
- Convert a ledger or reports between accounting standards (e.g. national vs IFRS).

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
   and entry amount. Thus we have no extra information for management accounting or
   detailed tax calculations.

6. Accounts balances can go to negative where they should not
   and there are little checks for entry validity.

7. XML likely to be a format for accounting reports interchange,
   while JSON is intended for `abacus`.

8. We use [just one currency](https://www.mscs.dal.ca/~selinger/accounting/).

9. Closing contra accounts and closing income summary account is stateful and needs careful
   implementation.

10. Account balances stay on one side, and do not migrate from one side to another.
    Credit accounts have credit balance, debit accounts have debit balance,
    and income summary account is a credit account.

11. Money amounts are integers, will move to `Decimal`.

12. Renamed account are dropped from the ledger. When `sales` becomes `net_sales` after a contra account `discount` is netted, `sales` leave the ledger, and `net_sales` remains.

## What things are realistic in this code?

1. Entries are stored in a queue and ledger state is calculated
   based on a previous state and a list of entries to be processed.

2. The chart of accounts can be fairly complex, up to a level of being GAAP/IAS 'compliant'.

3. Chart of accounts may include contra accounts. Temporary contra accounts
   for income (eg discounts given) and expense (discounts or cashbacks received)
   are cleared at period end, permanent contra accounts
   (e.g. accumulated depreciation) are carried forward.

4. You can give a name to typical dr/cr account pairs and use this name to record transactions.

5. Accounts can be renamed for reports, thus opening a way to internationalisation.
   Keep a short name like `cash` or account code in ledger and rename `cash` to `नकद` for a report.

## Implementation details

1. The code is covered by some tests, linted and type annotated.

2. Data structures used are serialisable, so inputs and outputs can be stored and retrieved.

3. Modern Python features such as subclasssing and pattern matching help to make code cleaner (hopefully). For example, classes like `Asset`, `Expense`, `Capital`, `Liability`, `Income` pass useful information about account types.

4. This is experimental software. The upside is that we can make big changes fast. On a downside we do not learn (or earn) from users, at least yet.

5. We do not compete with big names like SAP, Oralce, Intuit, smaller open source ERPs
   (Odoo, ERPNext, etc) or plain text accounting tools like `hledger` or `gnucash` in making a complete software product with journalling and document management.

## Similar projects

- [medici](https://github.com/flash-oss/medici) (JavaScript) is a ledger store, it allows compound entries and very optimized for high loads, but does not enforce any chart of accounts conventions.
- [pyluca](https://github.com/datasignstech/pyluca) is actively developed and has practical use in mind, coined a term 'headless ledger', has somewhat different interface and data structures than `abacus`.
- [ledger.py](https://github.com/mafm/ledger.py) started about 10 years ago with Python 2, once a [hledger](https://hledger.org/) rival, has good documentation, but last commit in 2018.
- There are few open source ERPs with accounting functionality under [`double-entry-accounting`](https://github.com/topics/double-entry-accounting) tag on Github.
- `Ledger`, `hledger` and `beancount` are leaders in [plain text accounting](https://plaintextaccounting.org/#tools)
- [gnucash](https://www.gnucash.org/)

## Feedback

... is much appreciated. Please reach out in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).
