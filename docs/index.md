# A minimal, yet valid double-entry accounting system in Python

`abacus` is an experimental package that aims to show that
accounting can be done with simple code.

With `abacus` you can perform complete accounting cycle,
including the following:

- define a chart of accounts,
- post entries to ledger,
- make trial balance and adjustment entries,
- close accounts at period end,
- produce balance sheet and income statement,
- carry account balances forward to the next period.

Currently, `abacus` exists as a Python package and a command line tool.
This means you can write you own Python code or short scripts
that would perform accounting operations.

`abacus` is particularly well suited for solving textbook examples,
that involve deciding on which accounting entries reflect business events.
There is a collection of textbook examples on this site. 

The big goal for `abacus` is to become a DSL (domain-specific language)
for accounting, in other words, a notation system that
allows to formulate accounting operations and demonstrate their results.
This system would be independent of a specific provider. 

## Minimal example

A firm starts business with a $5000 shareholder investment,
spends $1000 on marketing,
earns $3499 from clients,
and pays $2000 in salaries.

The Python code below will produce the balance sheet and income statement for the firm.

```python
from abacus import Chart, Report, echo

# Create a chart of accounts
chart = Chart(
    assets=["cash"],
    capital=["equity"],
    income=["services"],
    expenses=["marketing", "salaries"],
)

# Create a ledger using the chart
ledger = chart.ledger()

# Post entries to ledger
ledger.post(debit="cash", credit="equity", amount=5000)
ledger.post(debit="marketing", credit="cash", amount=1000)
ledger.post(debit="cash", credit="services", amount=3499)
ledger.post(debit="salaries", credit="cash", amount=2000)

# Print trial balance, balance sheet and income statement
report = Report(chart, ledger)
echo(report.trial_balance, "Trial balance")
echo(report.balance_sheet, "Balance sheet")
echo(report.income_statement, "Income statement")
print("Account balances:", report.account_balances)
```

This code can be found at [readme.py](readme.py).

<details>
    <summary>See the program output
    </summary>

```
(base) Q:\abacus>poetry run python readme.py

Trial balance
   Account    Debit  Credit
cash ........   5499      0
marketing ...   1000      0
salaries ....   2000      0
equity ......      0   5000
re ..........      0      0
services ....      0   3499
isa .........      0      0
null ........      0      0

Balance sheet
ASSETS... 5499  CAPITAL....... 5499
  Cash... 5499    Equity...... 5000
.........         Re..........  499
.........       LIABILITIES...    0
TOTAL:... 5499  TOTAL:........ 5499

Income statement
INCOME........... 3499
  Services....... 3499
EXPENSES:........ 3000
  Marketing...... 1000
  Salaries....... 2000
CURRENT PROFIT...  499

Account balances: {'cash': 5499, 'equity': 5000, 're': 0, 'services': 3499, 'marketing': 1000, 'salaries': 2000, 'isa': 0, 'null': 0}
```

</details>

## Accounting cycle

`abacus` enables to complete an accounting cycle in following steps.

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
