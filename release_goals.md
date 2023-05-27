# Next release: 0.3.0 Pipelines

A pipeline will allow to create lists of entries using commands
to close contra accounts as well as closing temporary ("nominal") accounts
(income, expense and income summary accounts) and will add current period
profit to retained earnings.

A pipeline will contain a start ledger (possibly empty ledger made from a chart of accounts), a list of postings to a ledger and methods to grow this list like
`add_entries()`, `.close_income()` or `.close_expenses()`.
These closing methods will add new postings to a list of postings, but creating a new ledger is postponed until all required entries are added to the list.

This enables composability of a pipeline, even though at a cost: a pipeline may need to execute internally to produce next ledger state. For example, to close income or expense accounts one must execute all postings to these accounts and find out the balance of this account.

The `run()` method will execute a pipeline py posting all entries to a start ledger. Pipeines should help to produce ledger states required for the income statement and balance sheet or other points in time of the accounting cylce.

Pipeines can be further optimised for performance, the initial implementation
disregards speed and computational intensity of a pipeline.

Affected issues are [#11](https://github.com/epogrebnyak/abacus/issues/11), [#10](https://github.com/epogrebnyak/abacus/issues/10) and [#7](https://github.com/epogrebnyak/abacus/issues/7).

# Release target: 0.4.0 CLI app with local json file backend

```console
# start project in current directory
abacus init .

# create ledger from chart
abacus ledger --chart chart.json > ledger.json

# create data store
abacus store --chart chart.json --ledger ledger.json > store.json

# add regular business entries
abacus entry --dr cash --cr equity --amount 1500 --title "Pay in shareholder capital" --push store.json
abacus entry --dr cash --cr sales --amount 160 --title "Accept payment for services" --push store.json
abacus entry --dr discounts --cr cash --amount 10 --title "Cashback on services" --push store.json
abacus entry --dr sga --cr cash --amount 25 --title "Incur selling expenses" --push store.json

# short hand entry (arguments, not options for dr, cr and amount)
abacus entry sga cash 5 --title "Adm. expenses" --push store.json

# get trial balance
abacus tb --store store.json > trial_balance.json

# net and purge contra accounts
abacus net --all --store store.json [--push | --show]

# close temporary accounts
abacus close --all --store store.json | abacus post --store.json

# process post-close entry
abacus entry --cr dividend_due --dr retained_earings --amount 60 --title "Accrue dividend" --post-close --push store.json

# produce income statement and balance sheet
abacus report --income-statement --store store.json > income_statement.json
abacus report --balance-sheet --store store.json --show

# write to and read from Excel file
abacus dump --store store.json --to-excel-file store.xlsx
abacus read --from-excel-file store_fix.xlsx > store_fix.json

# condense accounts to balances (similar to trail balance)
abacus balances --store store_fix.json > balances_fix.json

# create data store for next period
abacus store --chart chart.json --balances balances_fix.json > store2.json

# configuration: write to abacus.toml
abacus config set --store store.json --push store.json
abacus config remove --push
abacus config
```
