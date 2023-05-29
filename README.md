# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)

A minimal, yet valid double-entry accounting system in Python.

Check [release goals](release_goals.md) and [milestones](https://github.com/epogrebnyak/abacus/milestones) for upcoming features.

[mwe]: https://github.com/epogrebnyak/abacus#minimal-working-example

## What `abacus` should do

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

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

## CLI examples (upcoming in 0.4.0)

### Minimal

```bash
mkdir demo & cd demo
abacus init .
abacus set chart --assets cash,goods --expenses cogs,sga \
                 --capital equity --retained_earnings re \
                 --income sales
abacus post cash equity 5000
abacus post goods cash 1000
abacus post cash sales 350
abacus post goods cogs 250
abacus post sga cash 40
abacus close --all
abacus show report --income-statement
abacus show report --balance-sheet
```

### Extended

```bash
# Start project
mkdir books_2023 & cd books_2023  
abacus init . 

# Create chart of accounts
abacus set chart --assets cash,prepaid_rent,goods_for_sale,ppe \
                 --expenses overhead,cogs,sga,rent,interest \
                 --capital shareholder_equity \
                 --retained_earnings retained_earnings \
                 --income sales
abacus add accounts --liabilities loans dividend_due
abacus add contra-accounts discount cashback \
           --affect sales \ 
           --create net_sales 
abacus add contra-account depreciation --affects ppe --creates net_ppe 

# Add entries
abacus post cash shareholder_equity 2000 "Pay in shareholder capital"
abacus post prepaid_rent cash 240 "Prepay property rent (1 year)"
abacus post cash sales 880 "Service revenue (contract #306-2)"
abacus post sales discount 30 "Client discount (contract #306-2)"
abacus post sales cashback 50 "Client cashback (contract #306-2)"
abacus post sga cash 250 "Selling expenses"

# Close accounting period
abacus show trial-balance
abacus post --adjust prepaid_rent rent 60 "Accrue expenses (3 months)" 
abacus close --all
abacus post --after-close retained_earnings dividend_due 200 "Announced dividend" 

# Show reports
abacus name sga "Selling, general and adm.expenses"
abacus name cogs "Cost of goods sold"
abacus show report --income-statement
abacus show report --balance-sheet
abacus status
```

Anything missing? A gap in accounting logic? Louzy vairable name? Please [write to `abacus` author.](#feedback)

## Minimal working example (Python code)

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
    Entry("cash", "equity", 500),   # started a company
    Entry("cash", "sales", 150),    # selling services
    Entry("discounts", "cash", 30), # with a discount
    Entry("overhead", "cash", 50),  # and overhead expense
]
balance_sheet = (
    chart
    .set_retained_earnings_account("retained_earnings")
    .make_ledger()
    .process_entries(entries)
    .close()
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

2. Set retained earnings account, you will need it to close
   accoutns at period end.

```python
chart = chart.set_retained_earnings_account("re")
```

3. Next, create a general ledger based on chart of accounts.

```python
ledger = chart.make_ledger()
```

4. Add accounting entries using account names from the chart of accounts.

```python
e1 = Entry(dr="cash", cr="equity", amount=1000)        # pay in capital
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250) # acquire goods worth 250
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200) # sell goods worth 200
e4 = Entry(cr="sales", dr="cash", amount=400)          # for 400 in cash
e5 = Entry(cr="cash", dr="sga", amount=50)             # administrative expenses
ledger = ledger.process_entries([e1, e2, e3, e4, e5])
```

5. Make income statement at accounting period end.

```python
from abacus import IncomeStatement

income_statement = ledger.income_statement()
assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 50}
)
```

6. Close ledger and make balance sheet.

```python
from abacus import BalanceSheet

closed_ledger = ledger.close()
balance_sheet = closed_ledger.balance_sheet()
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"divp": 0, "payables": 0}
)
```

7. Print balance sheet and income statement to screen 
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

Check out [`readme.py`](readme.py) for a complete code example
with several contraccounts (depreciation, discounts) and dividend payout.

## Motivation

### Original intent

`abacus` started as a project to demonstrate principles of double-entry accounting
through Python code, in spirit of [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x).
You can use `abacus` to teach accounting and basics of accounting information systems (AIS).

### Other usage ideas

- Use with other software as a component, for example, add `medici` storage for entries (see below).
- Build business simulations - e.g. generate a stream of business events and make operational, financing and investment decisions based on financial report evaluation.
- Enhance a large language model with structured outputs in accounting.

## Assumptions

Below are some simplifying assumptions and behaviors made for this code.
Some points may be relaxes, some will remain a feature.

1. Account structure is flat, there are no subaccounts. (Can use `cash:petty` and `cash:bank_account`
   to mimic subaccounts.)

2. Every entry involves exactly two accounts, there are no compound entries.

3. No cash flow and changes in capital are reported.

4. There are no journals - all records go directly to general ledger.

5. Accounting entry is slim and has no information other than debit and credit accounts
   and entry amount. 

6. Accounts balances can go to negative where they should not and there are few checks for entry validity.

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
   for income (eg discounts given) and expense (discounts or cashbacks received)
   are cleared at period end, permanent contra accounts
   (e.g. accumulated depreciation) are carried forward.

4. You can give a name to typical dr/cr account pairs and use this name to record transactions.

5. Accounts can be renamed for reporting purposes, thus opening a way to internationalisation.
   You can keep a short name like `cash` or account code in ledger and rename `cash` to `नकद` for a report.

## Implementation details

1. The code is covered by some tests, linted and type annotated.

2. Data structures used are serialisable, so inputs and outputs can be stored and retrieved.

3. XML likely to be a format for accounting reports interchange,  while JSON and YAML are intended for `abacus`.

4. Modern Python features such as subclasssing and pattern matching help to make code cleaner. 
   Classes like `Asset`, `Expense`, `Capital`, `Liability`, `Income` pass forward useful information about account types and behaviors.

5. This is experimental software. The upside is that we can make big changes fast. On a downside we do not learn (or earn) from users, at least yet.

## Similar projects

JavaScript:

- [medici](https://github.com/flash-oss/medici) (JavaScript) is a ledger store optimized for high loads (does not enforce any chart of accounts conventions).

Python:

- [pyluca](https://github.com/datasignstech/pyluca) is actively developed and has practical use in mind, coined a term 'headless ledger' (different interface and data structures than `abacus`).
- [ledger.py](https://github.com/mafm/ledger.py) started about 10 years ago with Python 2, once a [hledger](https://hledger.org/) competitor, has good documentation, but last commit in 2018.

[Plain text accounting](https://plaintextaccounting.org/#tools):

- `Ledger`, `hledger` and `beancount` are leaders in [plain text accounting](https://plaintextaccounting.org/#tools)
- See also [gnucash](https://www.gnucash.org/)

More:

- Open source ERPs (Odoo, ERPNext) also have accounting functionality.
- [`double-entry-accounting`](https://github.com/topics/double-entry-accounting) tag on Github


## Feedback

... is much appreciated. Please reach out in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo). Would love to hear about accounting use cases for `abacus` 
(eg account inspection, reclassifications, etc). 

