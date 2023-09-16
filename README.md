# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)

A minimal, yet valid double-entry accounting system, provided as `abacus-py` Python package and the `bx` command line tool.

Using `abacus` you can:

- define a chart of accounts,
- post regular and adjustment entries to ledger,
- make trial balance,
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

Сreate temporary directory where `chart.json` and `entries.csv` will be created:

```
mkdir -p scripts/try && cd scripts/try
```

Create chart of accounts:

```bash
bx chart init
bx chart add --asset cash
bx chart add --asset ar --title "Accounts receivable"
bx chart add --asset goods --title "Inventory (goods for resale)"
bx chart add --asset prepaid_rent --title "Storage facility prepaid rent"
bx chart add --capital equity
bx chart add --liability dividend_due
bx chart add --income sales
bx chart offset sales discounts
bx chart add --expense cogs --title "Cost of goods sold"
bx chart add --expense sga --title "Selling, general and adm. expenses"
bx chart alias --operation invoice --debit ar --credit sales
bx chart alias --operation cost --debit cogs --credit goods
bx chart show
```

Start ledger, post entries and close accounts at period end:

```bash
bx ledger init
bx ledger post --debit cash  --credit equity --amount 5000 --title "Initial investment"
bx ledger post --debit goods --credit cash   --amount 3500 --title "Acquire goods for cash"
bx ledger post --debit prepaid_rent --credit cash --amount 1200 --title "Prepay rent"
bx ledger post --operation invoice 4300 cost 2500 --title "Issue invoice and register sales"
bx ledger post --debit discounts --credit ar --amount  450 --title "Provide discount"
bx ledger post --debit cash  --credit ar     --amount 3000 --title "Accept payment"
bx ledger post --debit sga   --credit cash   --amount  350 --title "Reimburse sales team"
bx ledger adjust --debit sga --credit prepaid_rent --amount 800 --title "Expense 8 months of rent"
bx ledger post-close --debit re --credit dividend_due --amount 150 --title "Accrue dividend"
bx ledger close
```

Make reports:

```bash
bx report --trial-balance
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

<details>
    <summary>Python code (`scripts/minimal.py`)
    </summary>

```python
from abacus import Chart, Entry, BalanceSheet, IncomeStatement

chart = (
    Chart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        equity=["equity", "re"],
        income=["sales"],
    )
    .offset("sales", "discounts")
    .set_name("cogs", "Cost of goods sold")
    .set_name("sga", "Selling, general and adm.expenses")
    .set_name("goods", "Inventory (goods for sale)")
    .set_name("ar", "Accounts receivable")
)

ledger = (
    chart.ledger()
    .post(Entry(debit="cash", credit="equity", amount=1000))
    .post(Entry(debit="goods", credit="cash", amount=800))
    .post(Entry(debit="ar", credit="sales", amount=465))
    .post(Entry(debit="discounts", credit="ar", amount=65))
    .post(Entry(debit="cogs", credit="goods", amount=200))
    .post(Entry(debit="sga", credit="cash", amount=100))
    .post(Entry(debit="cash", credit="ar", amount=360))
)

income_statement = ledger.income_statement(chart)
income_statement.print(chart.names)
income_statement.print_rich(chart.names)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)

ledger.close(chart)
balance_sheet = ledger.balance_sheet(chart)
balance_sheet.print(chart.names)
balance_sheet.print_rich(chart.names)
assert balance_sheet == BalanceSheet(
    assets={"cash": 460, "ar": 40, "goods": 600},
    capital={"equity": 1000, "re": 100},
    liabilities={},
)

# Create end of period balances
end_balances = ledger.nonzero_balances()
print(end_balances)
next_book = chart.ledger(starting_balances=end_balances)
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
