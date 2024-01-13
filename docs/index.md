<img width="64" align="right" src="assets/robot.png">

# Minimal, yet valid double-entry accounting system in Python and command line

`abacus` is an Python package and a command line tool for accounting calculations.

With `abacus` you can perform a complete accounting cycle
from a chart of accounts to financial reports.
To start using `abacus` go to [Quick Start](quick_start.md) section.

Few lines of sample code for a fictious [Dunder Mufflin paper company](https://en.wikipedia.org/wiki/Dunder_Mifflin) are listed below together with `abacus` outputs.

=== "Python"

    ```python

    from abacus import Chart, Account, Report

    # Define chart
    chart = Chart(
        assets=["cash", "paper"],
        capital=["equity"],
        income=[Account("sales", contra_accounts=["refunds"])],
        expenses=["cogs", "salaries"],
    )

    # Use account balances form previous period
    starting_balances = {"cash": 300, "paper": 2200, "equity": 2500}
    ledger = chart.ledger(starting_balances)

    # Post enties
    ledger.post("cash", "sales", 2675, title="Sell paper for cash")
    ledger.post("refunds", "cash", 375, title="Client refund")
    ledger.post("cogs", "paper", 2000, title="Register cost of sales")
    ledger.post("salaries", "cash", 500, title="Pay salaries")

    # Show reports
    rename_dict = {"cogs": "Cost of goods sold", "paper": "Inventory"}
    report = Report(chart, ledger, rename_dict)
    report.print_all()
    ```

=== "Command line"

    ```bash
    bx init
    abacus add asset:cash
    abacus add asset:paper --title "Inventory"
    abacus add capital:equity
    abacus add income:sales contra:sales:refunds
    abacus add expense:cogs --title "Cost of goods sold"
    abacus add expense:salaries
    echo {\"cash\": 300, \"paper\": 2200, \"equity\": 2500} > starting_balances.json
    abacus load starting_balances.json
    abacus post cash     sales 2675 --title="Sell paper for cash"
    abacus post refunds  cash   375 --title="Client refund"
    abacus post cogs     paper 2000 --title="Register cost of sales"
    abacus post salaries cash   500 --title="Pay salaries"
    abacus close
    abacus report --all
    ```

=== "Trial balance"

    ```
                Trial balance
    Account                   Debit   Credit
    cash                       2100        0
    paper                       200        0
    refunds                     375        0
    cogs                       2000        0
    salaries                    500        0
    equity                        0     2500
    retained_earnings             0        0
    sales                         0     2675
    _isa                          0        0
    _null                         0        0
    ```

=== "Balance sheet"

    ```
                Balance sheet
    Assets       2300   Capital          2300
      Cash       2100     Equity         2500
      Inventory   200     Retained       -200
                          earnings
                        Liabilities         0
    Total        2300  Total             2300
    ```

=== "Income statement"

    ```
                Income Statement
    Income                              2300
      Sales                             2300
    Expenses                            2500
      Cost of goods sold                2000
      Salaries                           500
    Current profit                      -200
    ```

=== "Install"

    ```
    pip install abacus-py
    ```

[Quick Start](quick_start.md){ .md-button .md-button--primary }
