# Quick start

## Install

`abacus` requires Python 3.10 or higher. To install run in the command line:

```
pip install abacus-py
```

## Accounting cycle with `abacus`

With `abacus` you can do the following parts of accounting work:

1. define a chart of accounts,
2. post entries to ledger,
3. make trial balance and adjustment entries,
4. close accounts at period end,
5. make balance sheet and income statement.

## Minimal example

A trading firm started with $5000 investment from shareholders,
bought $4000 worth of merchandise and sold it for $4800,
also paid $500 to the firm sales representative.
Show firm balance sheet and income statement at period end.

### Define chart of accounts

=== "Python"

    ```python
    from abacus import Chart

    chart = Chart(
        assets=["cash", "inventory"],
        capital=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        retained_earnings_account="retained_earnings"
    )
    ```

=== "Command line"

    ```bash
    abacus init
    abacus add asset:cash,inv
    abacus add capital:equity
    abacus add income:sales expense:cogs,sga
    abacus name inv "Inventory"
    abacus name cogs "Cost of goods sold"
    abacus name sga "Selling expenses"
    ```

### Use ledger to post entries

=== "Python"

    ```python
    ledger = chart.ledger()
    ledger.post("cash", "equity", 5000, title="Shareholder investment")
    ledger.post("inventory", "cash", 4000, title="Purchased merchandise")
    ledger.post("cash", "sales", 4800, title="Sold merchandise")
    ledger.post("cogs", "inventory", 4000, title="Registered cost of sales")
    ledger.post("sga", "cash", 500, title="Paid sales representative")
    ```

=== "Command line"

    ```bash
    abacus post cash equity 5000 --title "Shareholder investment"
    abacus post  inv   cash 4000 --title "Purchased merchandise"
    abacus post cash  sales 4800 --title "Sold merchandise"
    abacus post cogs    inv 4000 --title "Registered cost of sales"
    abacus post  sga   cash  500 --title "Paid sales representative"
    abacus close
    ```

### Make reports

=== "Python"

    ```python
    from abacus import Report
    report = Report(chart, ledger)
    report.balance_sheet.print()
    report.income_statement.print()
    ```

=== "Command line"

    ```bash
    abacus report --balance-sheet
    abacus report --income-statement
    ```

Complete file listings may be found at [quick_start.py](quick_start.py)
and [quick_start.sh](quick_start.sh).
