# Quick start

## Install

`abacus` requires Python 3.10 or higher. To install run in the command line:

```
pip install abacus-py
```

## Accounting cycle with `abacus`

With `abacus` you can replicate the following parts of accounting work:

- [x] define a chart of accounts,
- [x] post entries to ledger,
- [x] make trial balance and adjustment entries,
- [x] close accounts at period end,
- [x] make balance sheet and income statement.

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
        assets=["cash", "inv"],
        capital=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        retained_earnings_account="retained_earnings"
    )
    ```

=== "Command line"

    ```bash
    bx init
    bx chart add --asset cash
    bx chart add --asset inv --title "Inventory"
    bx chart add --capital equity
    bx chart add --income sales
    bx chart add --expense cogs --title "Cost of goods sold"
    bx chart add --expense sga --title "Selling expenses"
    ```

### Use ledger to post entries

=== "Python"

    ```python
    ledger = chart.ledger()
    ledger.post(debit="cash", credit="equity", amount=5000, title="Shareholder investment")
    ledger.post("inv",  "cash",   4000, title="Purchased merchandise")
    ledger.post("cash", "sales",  4800, title="Sold merchandise")
    ledger.post("cogs", "inv",    4000, title="Registered cost of sales")
    ledger.post("sga",  "cash",    500, title="Paid sales representative")
    ```

=== "Command line"

    ```bash
    bx post --entry cash equity 5000 --title "Shareholder investment"
    bx post --entry  inv   cash 4000 --title "Purchased merchandise"
    bx post --entry cash  sales 4800 --title "Sold merchandise"
    bx post --entry cogs    inv 4000 --title "Registered cost of sales"
    bx post --entry  sga   cash  500 --title "Paid sales representative"
    bx close
    ```

### Make reports

=== "Python"

    ```python
    from abacus import Report
    report = Report(chart, ledger)
    report.trial_balance.viewer.print()
    report.balance_sheet.viewer.print()
    report.income_statement.viewer.print()
    print(report.account_balances)
    ```

=== "Command line"

    ```bash
    bx report --balance-sheet
    bx report --income-statement
    ```

<!--
Complete file listings may be found at
[quick_start.py](https://github.com/epogrebnyak/abacus/blob/main/docs/quick_start.py)
and [quick_start.bat](https://github.com/epogrebnyak/abacus/blob/main/docs/quick_start.bat).
-->

## More features

### Contra accounts

```bash
bx chart add contra:sales:refunds
bx chart offset sales voids
bx post --entry refunds cash 120 --title "Client refund"
```

### Trial balance

```bash
bx report --trial-balance
```

### Account balances

```bash
bx show balances
bx show balances --nonzero > balances.json
```

In your next project you can do `bx ledger load balances.json`.

### Help with `abacus`

```
bx --help
```
