# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)

A minimal, yet valid double-entry accounting system, provided as `abacus-py` Python package and the `bx` command line tool.

Using `abacus` you can:

- define a chart of accounts,
- create general ledger,
- post accounting entries,
- close accounts at period end,
- produce trial balance, balance sheet and income statement.

## Quotes about `abacus`

[![Reddit Discussion](https://img.shields.io/badge/Reddit-%23FF4500.svg?style=for-the-badge&logo=Reddit&logoColor=white)](https://www.reddit.com/r/Accounting/comments/136rrit/wrote_an_accounting_demo_in_python/)

> I think it's a great idea to mock-up a mini GL ERP to really get a foundational understanding of how the accounting in ERP works!

> I teach accounting information systems... I'd be tempted to use abacus as a way of simply showing the structure of a simple AIS.

> Hey, what a cool job, thanks much. Do you plan to make a possibility for RAS accounting?

## Install

```
pip install abacus-py
```

For latest version install from github:

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

This will install both `abacus-py` package and the `bx` command line tool.

`abacus-py` requires Python 3.10 or higher.

## Minimal command line example

Install package and create temporary directory:

```bash
pip install -U abacus-py
mkdir try_abacus && cd try_abacus
```
Create chart of accounts:

```bash
bx chart set --asset cash
bx chart set --asset ar --title "Accounts receivable"
bx chart set --asset goods --title "Inventory (goods for resale)"
bx chart set --capital equity
bx chart set --retained-earnings re
bx chart set --income sales
bx chart offset --account sales --contra-accounts discounts
bx chart set --expense cogs --title "Cost of goods sold"
bx chart set --expense sga --title "Selling, general and adm. expenses"
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
    <summary>Python code
    </summary>

```python
import abacus
# Add Python code here
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
