# abacus

[![pytest](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml/badge.svg)](https://github.com/epogrebnyak/abacus/actions/workflows/.pytest.yml)
[![PyPI](https://img.shields.io/pypi/v/abacus-py?color=blue)](https://pypi.org/project/abacus-py/)

A minimal, yet valid double-entry accounting system in Python.

With `abacus` you can:

- define a chart of accounts,
- post entries to ledger,
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

For latest version install from github:

```
pip install git+https://github.com/epogrebnyak/abacus.git
```

`abacus-py` requires Python 3.10 or higher.

## Command line tools

There are two command line tools available after you install this package: `abacus` and `cx`.
You can check them as:

```bash
abacus --help
cx --help
```

`abacus` has a full set of commands and options, while `cx` is just several commands with a more simple syntax.
`cx` is ideal for solving textbook exercises.
Both tools enable to complete a full accounting cycle and share the same data model.
They create and modify two files `chart.json` and `entries.linejson` in your project folder.

## The `cx` command line tool

With `cx` command line tool the entire accounting cycle can be performed using just five commands:

| Command  | What it does                                            |
| -------- | ------------------------------------------------------- |
| `init`   | Start new project in empty folder.                      |
| `post`   | Post a double entry to ledger.                          |
| `close`  | Add closing entries to ledger at accounting period end. |
| `name `  | Set descriptive title for an account.                   |
| `report` | Show trial balance, balance sheet or income statement.  |

Here is how the key `cx` commands compare with `abacus` commands:

| `cx`            | `abacus`                                                        |
| --------------- | --------------------------------------------------------------- |
| `cx init`       | `abacus chart init && abacus ledger init`                       |
| `cx post`       | `abacus ledger post`                                            |
| `cx close`      | `abacus ledger close`                                           |
| `cx name`       | `abacus chart name`                                             |
| `cx report -t`  | `abacus report trial-balance`                                   |
| `cx report -ib` | `abacus report income-statement && abacus report balance-sheet` |
| `cx unlink`     | `abacus chart unlink && abacus ledger unlink`                   |

### Textbook example

Here is an exercise from "Accounting Principles" by Weygandt, Kimmel and Kieso
(ed 12, p. 31) solved with `cx`.

> Joan Robinson opens her own law office on July 1, 2017. During the first month of operations, the following transactions occurred.
>
> 1. Joan invested $11,000 in cash in the law practice.
> 2. Paid $800 for July rent on offi ce space.
> 3. Purchased equipment on account $3,000.
> 4. Performed legal services to clients for cash $1,500.
> 5. Borrowed $700 cash from a bank on a note payable.
> 6. Performed legal services for client on account $2,000.
> 7. Paid monthly expenses: salaries and wages $500, utilities $300, and advertising $100.
> 8. Joan withdrew $1,000 cash for personal use.

Here is a complete code to solve the exercise:

```
cx init
cx post --debit asset:cash               --credit capital:equity --amount 11000
cx post --debit expense:rent             --credit cash           --amount 800
cx post --debit asset:equipment          --credit liability:ap   --amount 3000
cx post --debit cash                     --credit income:sales   --amount 1500
cx post --debit cash                     --credit liability:note --amount 700
cx post --debit asset:ar                 --credit sales          --amount 2000
cx post --debit expense:salaries         --credit cash           --amount 500
cx post --debit expense:utilities        --credit cash           --amount 300
cx post --debit expense:ads              --credit cash           --amount 100
cx post --debit contra:equity:withdrawal --credit cash           --amount 1000
cx name ar "Accounts receivable"
cx name ap "Accounts payable"
cx name ads "Advertising"
cx report --trial-balance
cx close
cx report --balance-sheet
cx report --income-statement
```

<details>
    <summary>See the program output
    </summary>

```
Balance sheet
ASSETS.................. 15500  CAPITAL............... 11800
  Cash.................. 10500    Equity.............. 10000
  Equipment.............  3000    Retained earnings...  1800
  Accounts receivable...  2000  LIABILITIES...........  3700
........................          Accounts payable....  3000
........................          Note................   700
TOTAL:.................. 15500  TOTAL:................ 15500

Income statement
INCOME........... 3500
  Sales.......... 3500
EXPENSES......... 1700
  Rent...........  800
  Salaries.......  500
  Utilities......  300
  Advertising....  100
CURRENT PROFIT... 1800
```

Issue [#49](https://github.com/epogrebnyak/abacus/issues/49) has additional information about this example.

</details>

### Note about account names

The `post` command accepts account names under following rules:

- **Оne colon**: (`asset:cash`) is account type and name seperated by colon (`:`).
  Valid account types are `asset`, `capital`, `liability`, `income`, `expense`,
  or plural forms where appropriate. When first encountered, the account name
  is added to the chart of accounts. Account names should be unique, you cannot
  have `cash:other` and `capital:other` in chart.
- **Two colons starting with `contra`**. In example `contra:equity:withdrawal`
  the new account name is `withdrawal`. This new account will be added
  to chart as a contra acccount to `equity` account.
- **No colon**: Short names like `cash`, `sales`, `withdrawal` without colon
  can be used in `post` command after the account name was added to chart.

## The `abacus` command line tool

The `abacus` command line tool has a more verbose interface than `cx`.

Let's go through an example.

### Working directory

Сreate temporary directory:

```
mkdir try_abacus
cd try_abacus
```

### Chart of accounts

Create chart of accounts using the following:

- `chart init` for new chart
- `chart add` for regular accounts
- `chart offset` for contra accounts
- `chart promote` for adding accounts by labels
- `chart alias` for naming operations
- `chart show` to print chart

```bash
abacus chart init
abacus chart add --asset cash
abacus chart add --asset ar --title "Accounts receivable"
abacus chart add --asset goods --title "Inventory (goods for resale)"
abacus chart add --asset prepaid_rent --title "Storage facility prepaid rent"
abacus chart add --capital equity
abacus chart add --liability dividend_due
abacus chart add --income sales
abacus chart offset sales discounts
abacus chart add --expense cogs --title "Cost of goods sold"
abacus chart add --expense sga --title "Selling, general and adm. expenses"
abacus-extra alias add --operation invoice --debit ar --credit sales
abacus-extra alias add --operation cost --debit cogs --credit goods
abacus chart show
```

At this point you will see `chart.json` created:

```bash
cat chart.json
```

### Ledger

Start ledger, post entries and close accounts at period end:

```bash
abacus ledger init
abacus ledger post --debit cash  --credit equity --amount 5000 --title "Initial investment"
abacus ledger post --debit goods --credit cash   --amount 3500 --title "Acquire goods for cash"
abacus ledger post --debit prepaid_rent --credit cash --amount 1200 --title "Prepay rent"
abacus-extra alias post --operation invoice 4300 --operation cost 2500 --title "Issue invoice and register sales"
abacus ledger post --debit discounts --credit ar --amount  450 --title "Provide discount"
abacus ledger post --debit cash  --credit ar     --amount 3000 --title "Accept payment"
abacus ledger post --debit sga   --credit cash   --amount  300 --title "Reimburse sales team"
abacus ledger post --debit sga --credit prepaid_rent --amount 800 --title "Expense 8 months of rent"
abacus ledger close
abacus ledger post --debit re --credit dividend_due --amount 150 --title "Accrue dividend"
```

At this point you will see `entries.linejson` created:

```bash
cat entries.linejson
```

### Reports

Produce and print to screen the trial balance, balance sheet and income statement reports.

```bash
abacus report trial-balance
abacus report balance-sheet
abacus report income-statement
```

The results for balance sheet and income statement should look similar to this:

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

### Inspect individual accounts

`account show` command will show detailed information about a specific account.

```bash
abacus account show sales
```

`account assert` is useful in testing as it makes sure account balance equals
specified value.

```bash
abacus account assert --balance cash 3000 --balance ar 850 --balance goods 1000
```

### Account balances

Print a JSON file with account names and account balances.

```bash
abacus account show-balances --nonzero
```

This command is used in carrying balances forward to next period.

```
# save output to end.json
abacus account show-balances --nonzero > end.json

# copy end.json and chart.json to a new folder and do:
abacus ledger init end.json
```

<details>
    <summary>Python code (`scripts/minimal.py`)
    </summary>

```python
from abacus import BaseChart, Entry, BalanceSheet, IncomeStatement

chart = (
    BaseChart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        capital=["equity", "re"],
        income=["sales"],
    ).elevate()
    .set_isa("current_profit")
    .set_null("null")
    .set_re("re")
    .offset("sales", "discounts")
    .name("cogs", "Cost of goods sold")
    .name("sga", "Selling, general and adm.expenses")
    .name("goods", "Inventory (goods for sale)")
    .name("ar", "Accounts receivable")
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
income_statement.print(chart.titles)
income_statement.print_rich(chart.titles)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)

ledger.close(chart)
balance_sheet = ledger.balance_sheet(chart)
balance_sheet.print(chart.titles)
balance_sheet.print_rich(chart.titles)
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

Your feedback is highly appreciated and should help steering `abacus` development.

## Contributions

### Program design

`abacus` is designed around core accounting concepts such as
chart of accounts, general ledger, accounting entry and financial reports.
These concepts correspond to classes created inside `abacus`:
`Chart`, `Ledger`, `Entry`, `BalanceSheet` and `IncomeStatement`.

Here is a workflow scetch under which these classes interact:

- you add new accounts to `Chart` indicating the account type,
- from `Chart` you create empty `Ledger`,
- an `Entry` or a list of entries `[Entry]` is posted to `Ledger`,
- there is a procedure to create a list of closing entries for `Ledger`
  at period end,
- these closing entries are posted to ledger,
- from `Ledger` you can get account balances,
- the account balances are used to create trial balance, `BalanceSheet` and
  `IncomeStatement`.

You need to import just `abacus.Chart` and `abacus.Entry`
classes to write code for the entire accounting cycle as other classes
(`Ledger`, balances, `BalanceSheet` and `IncomeStatement`) will be derived form
`Chart` and `Entry`.

In the sequence above the most tricky part is probably the closing entries,
thus special care is given to documenting them in the `abacus.closing` module.

`abacus` type system also handles contra accounts, for example
property, plant and equipment account is an instance of `Asset` class, while
depreciation is a `ContraAsset` class instance. The temporary contra accounts
(those accounts that offsett `Income` and `Expense`) will be closed at period end,
while permanent contra accounts (offsetting `Asset`, `Equity` and `Liability`)
will be carried forward to next period to preserve useful information.

For storage we persist just the chart and the entries posted. We do not save the
state of the ledger. Given the chart (from `chart.json` file) and
accounting entries (from the `entries.json` file) we can calculate
ledger state at any time. This state may be cached to speed up retieval
of balances in a bigger systems (see [solution used in `medici` package][cache]).

[cache]: https://github.com/flash-oss/medici#fast-balance

If you into functional programming, the entire type signature for
`abacus` is the following:

```
Chart -> [Entry] -> Ledger -> [ClosingEntry] -> Ledger -> (BalanceSheet, IncomeStatement)
```

1. start with chart
2. add a list of entries
3. create ledger
4. calualte closing entries
5. post closing entries to ledger
6. calculate balance sheet and income statement

In general, what `abacus` (or any other double entry accounting program) does
is maintaining an extended accounting equation in balance.
If you are comfortable with this idea, the rest of program flow and code
should be more easy to follow.

Note that real ERP and accounting systems do a lot more than double entry accounting,
for example keeping the original document references and maintaining identities
of the clients and suppliers as well as keeping extra data about contracts and
whatever management accounting may need to have a record of (for example, your inventory).

Most of this funcitonality is out of scope for a double entry ledger.
We just need a chart of accounts, create a ledger based on chart,
post entries that have information about debit account, credit account and amount,
close ledger at period end and produce financial reports,
plus allow creating a trail balance and doing adjustment
and post-close entries if needed.

### Testing

You will need [just command runner](https://github.com/casey/just)
and [poetry package manager](https://python-poetry.org/) for developing
`abacus`.

All commands for testing I gather in `just grill` command.
This command will launch:

- `pytest` for unit tests
- `mypy` to check type annotations
- `isort` to sort imports
- `black` for code formatting
- `ruff` for code check and linting
- `prettier` to clean markdown files
- extracting and running code from README.md
- a few bash scripts to test the `abacus` and `cx` command line tools.

I found that testing CLI with bash files, one for chart, ledger, reports and
inspect commands, accelerates the development workflow.

## Changelog

### 0.7.6

- `ledger post-compound` method added
- `bx` tool depreciated and replaced by `abacus` CLI

### 0.7.3

- `click` package used for new CLI entrypoint called `abacus` (will replace `abacus` tool)
- parts of CLI code moved to `abacus.cli`
- targeting fuller `abacus` and minimal 5 command `ex` command line tools

### 0.7.0

The `cx` command line tool enables to run entire accounting cycle from postings to reports with just five commands:

- `init` - start new project in folder,
- `post` - post accounting entry with debit account, credit account and transaction amount,
- `close` - post closing entries at accounting period end,
- `name` - specify verbose account names for reports, and
- `report` - show trial balance, balance sheet or income statement.

There is a textbook example from Principles of Accounting textbook by Weygandt, Kimmel and Kieso - the starting of Joan Robinson law office (ed 12, p. 31). There are 11 transactions in the excercise and under 20 lines of code to solve it with `abacus`,
[check it out](https://github.com/epogrebnyak/abacus#textbook-example)!

Posted the changelog to Reddit as <https://www.reddit.com/r/Python/comments/178kgyu/github_epogrebnyakabacus_run_full_doubleentry/>
