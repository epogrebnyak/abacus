# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)

A minimal, yet valid double-entry accounting system, provided as `abacus-py` Python package and the `bx` command line tool.

Using `abacus` you can:

- define a chart of accounts,
- create general ledger,
- post accounting entries,
- close accounts at period end,
- produce balance sheet and income statement.

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install abacus-py
```

This will install both `abacus-py` package and the `bx` command line tool.

For latest version install from github:

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

`abacus-py` requires Python 3.10 or higher.

## Minimal command line example

Install package and create temporary directory:

```bash
pip install -U abacus-py
mkdir try_abacus && cd try_abacus
```
Create chart of accounts:

```bash
bx chart add --asset cash
bx chart add --asset ar --title "Accounts receivable"
bx chart add --asset goods --title "Inventory (goods for resale)"
bx chart add --capital equity
bx chart add --retained-earnings re
bx chart add --income sales
bx chart offset sales discounts
bx chart add --expense cogs --title "Cost of goods sold"
bx chart add --expense sga --title "Selling, general and adm. expenses"
bx chart show
```

Start ledger, post entries and close accounts at period end:

```bash
bx ledger start
bx post entry --title "Initial investment"     --debit cash  --credit equity --amount 5000
bx post entry --title "Acquire goods for cash" --debit goods --credit cash   --amount 4000
bx post entry --title "Register cost of sales" --debit cogs  --credit goods  --amount 2700
bx post entry --title "Issue invoice"          --debit ar    --credit sales  --amount 3900
bx post entry --title "Provide discount"       --debit discounts --credit ar --amount  400
bx post entry --title "Accept payment"         --debit cash  --credit ar     --amount 2000
bx post entry --title "Reimburse sales team"   --debit sga   --credit cash   --amount  300
bx ledger close
```

Make reports:

```bash
bx report --balance-sheet
bx report --income-statement
```

The results should look similar to this:

```
Balance sheet
Assets                          5500  Capital              5500
- Cash                          2700  - Equity             5000
- Accounts receivable           1500  - Retained earnings   500
- Inventory (goods for resale)  1300  Liabilities             0
Total                           5500  Total                5500

Income statement
Income                                                     3500
- Sales                                                    3500
Expenses                                                   3000
- Cost of goods sold                                       2700
- Selling, general and adm. expenses                        300
Profit                                                      500
```

Additional features include entry templates (`operation` command), adjustment
and post-close entries.

<details>
    <summary>Python code (`examples/readme/minimal.py`)
    </summary>

```python
from abacus import BalanceSheet, Chart, IncomeStatement, PlainTextViewer, RichViewer

chart = (
    Chart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        equity=["equity", "re"],
        income=["sales"],
    )
    .set_retained_earnings("re")
    .offset("sales", "discounts")
    .set_name("cogs", "Cost of goods sold")
    .set_name("sga", "Selling, general and adm.expenses")
    .set_name("goods", "Inventory (goods for sale)")
    .set_name("ar", "Accounts receivable")
)

book = (
    chart.book()
    .post(debit="cash", credit="equity", amount=1000)
    .post(debit="goods", credit="cash", amount=800)
    .post(debit="ar", credit="sales", amount=465)
    .post(debit="discounts", credit="ar", amount=65)
    .post(debit="cogs", credit="goods", amount=200)
    .post(debit="sga", credit="cash", amount=100)
    .post(debit="cash", credit="ar", amount=360)
    .close()
)

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
tv = PlainTextViewer(rename_dict=chart.names)
tv.print(balance_sheet)
tv.print(income_statement)

rv = RichViewer(rename_dict=chart.names, width=80)
rv.print(balance_sheet)
rv.print(income_statement)

print(income_statement)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
    assets={"cash": 460, "ar": 40, "goods": 600},
    capital={"equity": 1000, "re": 100},
    liabilities={},
)

# Create next period
end_balances = book.nonzero_balances()
print(end_balances)
next_book = chart.book(starting_balances=end_balances)
```

</details>

## Documentation

<https://epogrebnyak.github.io/abacus/>

## Feedback

Anything missing in `abacus`?
Got a good use case for `abacus` or used `abacus` for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering `abacus` development.
