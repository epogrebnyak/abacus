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

### 0.7.8

- adds label handling like `asset:cash`, `contra:sales:refunds` and `re:retained_earnings`
- fixes VAT example

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
