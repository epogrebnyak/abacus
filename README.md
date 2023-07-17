# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)

A minimal, yet valid double-entry accounting system, provided as `abacus-py` Python package and `bx` command line tool.

Using `abacus` you can:

- define a chart of accounts, 
- create general ledger,
- post accounting entries,
- close accounts at period end, 
- produce trial balance, balance sheet and income statement.

A minimal command line example is below:

```bash
pip install -U abacus-py
mkdir try_abacus && cd try_abacus
bx chart set --asset cash
bx chart set --asset ar --title "Accounts receivable"
bx chart set --asset goods --title "Inventory (goods for resale)"
bx chart set --capital equity
bx chart set --retained-earnings re
bx chart set --income sales
bx chart set --expense cogs --title "Cost fo goods sold"
bx chart set --expense sga --title "Selling, general and adm. expenses"
bx ledger start
bx post entry --title "Initial investment"     --debit cash  --credit equity --amount 5000
bx post entry --title "Acquire goods for cash" --debit goods --credit cash   --amount 4000
bx post entry --title "Register cost of sales" --debit cogs  --credit goods  --amount 2500
bx post entry --title "Issue invoice"          --debit ar    --credit sales  --amount 3500
bx post entry --title "Accept payment"         --debit cash  --credit ar     --amount 2000
bx post entry --title "Paid sales team salary" --debit sga   --credit cash   --amount  500
bx ledger close
bx report --balance-sheet
bx report --income-statement
```

Additional features include contra accounts (`offset` command) 
and entry templates (`operation` command).

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

## Example

A freshly created trading Klondike Trading Company (KTC) has recorded the following transactions.

|     | Transaction Title                         |        Debit        |       Credit        | Amount |
| --- | ----------------------------------------- | :-----------------: | :-----------------: | -----: |
| 1   | Shareholders paid up capital contribution |        Cash         |       Equity        |   1000 |
| 2   | Purchased goods for resale                |      Inventory      |        Cash         |    800 |
| 3   | Invoiced client on sales contract         | Accounts Receivable |       Revenue       |    465 |
| 4   | Provided discount to client               |      Discounts      | Accounts Receivable |     65 |
| 5   | Recorded cost of sales                    |        COGS         |      Inventory      |    200 |
| 6   | Paid salary to contract manager           |    SG&A Expenses    |        Cash         |    100 |
| 7   | Accepted payment on sales contract        |        Cash         | Accounts Receivable |    360 |

After closing accounts the company announced, but has not paid dividend.

|     | Transaction Title                   |       Debit       |    Credit    | Amount |
| --- | ----------------------------------- | :---------------: | :----------: | -----: |
| \*  | Accrued dividend after announcement | Retained Earnings | Dividend Due |     50 |

### 1. Chart

Define a chart of accounts of five types (assets, equity, liabilities, income and expenses),
specify retained earnings account name and, optionally, add contra accounts.

```python
from abacus import Chart

chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["dividend_due"],
    income=["sales"])
chart = chart.set_retained_earnings("re").offset("sales", "discounts")
```

### 2. Ledger

Create a general ledger based on the chart of accounts,
post entries and close accounts at accounting period end.

```python
book = (chart.book()
  .post(debit="cash", credit="equity", amount=1000)
  .post(debit="goods", credit="cash", amount=800)
  .post(debit="ar", credit="sales", amount=465)
  .post(debit="discounts", credit="ar", amount=65)
  .post(debit="cogs", credit="goods", amount=200)
  .post(debit="sga", credit="cash", amount=100)
  .post(debit="cash", credit="ar", amount=360)
  .close()
  .after_close(debit="re", credit="dividend_due", amount=50)
)
```

### 3. Reports

Make trail balance, income statement and balance sheet and save or print them to screen
with verbose account names and rich text formatting.

```python
from abacus import RichViewer, PlainTextViewer

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}

tv = PlainTextViewer(rename_dict)
tv.print(balance_sheet)
tv.print(income_statement)

rv = RichViewer(rename_dict, width=80)
rv.print(balance_sheet)
rv.print(income_statement)
```

The output should look similar to text and a screenshot below.

```
Assets                        1100  Capital              1050
- Cash                        460   - Equity             1000
- Accounts receivable         40    - Retained earnings    50
- Inventory (goods for sale)  600   Liabilities            50
                                    - Dividend due         50
Total                         1100  Total                1100

Income                                400
- Sales                               400
Expenses                              300
- Cost of goods sold                  200
- Selling, general and adm. expenses  100
Profit                                100
```

<details>
<summary> Screenshot (outdated).
</summary>

![](https://user-images.githubusercontent.com/9265326/249445794-7def0fc2-934b-49fa-a3ad-9137072a2900.png)

</details>

<details>
<summary> Details about correctness checks and end balances.
</summary>

### Check values

As a reminder `assert` statement in Python will raise exception if provided wrong comparison.
These checks will execute and this way we will know the code in README is up to date and correct.

```python
from abacus import IncomeStatement, BalanceSheet

print(income_statement)
assert income_statement == IncomeStatement(
    income={'sales': 400},
    expenses={'cogs': 200, 'sga': 100}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
  assets={'cash': 460, 'ar': 40, 'goods': 600},
  capital={'equity': 1000, 're': 50},
  liabilities={'dividend_due': 50}
)
```

### End balances

You can use end balances from current period to initialize ledger at the start of next accounting period.

```python
end_balances = book.nonzero_balances()
print(end_balances)
next_book = chart.book(starting_balances=end_balances)
```

</details>

## Command line

Similar operations with chart, ledger and reports can be performed on the command line.

### Create chart of accounts

```bash
bx erase --chart
bx chart set --asset cash
bx chart set --asset ar --title "Accounts receivable"
bx chart set --asset goods --title "Inventory (good for sale)"
bx chart set --capital equity
bx chart set --retained-earnings re
bx chart set --liability dividend_due
bx chart set --income sales
bx chart set --expense cogs --title "Cost of sales"
bx chart set --expense sga --title "Selling expenses"
bx chart offset sales discounts
bx chart show
```

### Post entries to ledger and close

```bash
bx erase --ledger
bx ledger start
bx post entry --debit cash      --credit equity --amount 1000
bx post entry --debit goods     --credit cash   --amount 800
bx post entry --debit ar        --credit sales  --amount 465
bx post entry --debit discounts --credit ar     --amount 65
bx post entry --debit cogs      --credit goods  --amount 200
bx post entry --debit sga       --credit cash   --amount 100
bx post entry --debit cash      --credit ar     --amount 360
bx ledger close
bx post entry --debit re --credit dividend_due --amount 50 --after-close
```

### Report

```bash
bx report --balance-sheet
bx report --income-statement
```

### Account information

```bash
bx account cash
bx account ar
bx account goods
bx account sales
bx accounts
```

You can save end balances to a file and initialize next period ledger.

```bash
bx accounts --json > end_balances.json
```

`assert` command will complain if account balance is not equal to provided value.
This is useful for testing.

```bash
bx assert cash 460
```

## Feedback

Anything missing in `abacus`?
Got a good use case for `abacus` or used `abacus` for teaching?

Feel free to contact `abacus` author
in [issues](https://github.com/epogrebnyak/abacus/issues),
on [reddit](https://www.reddit.com/user/iamevpo)
or via [Telegram](https://t.me/epoepo).

Your feedback is highly appreciated and helps steering development of `abacus`.
