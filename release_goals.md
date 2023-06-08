# Release target: 0.5.0 CLI app

- testing of a multiline string `pytest-console-plugin`
- golden tests
- `names` command
- colored output with --rich flag
- configuration: write to abacus.toml
- title for entry
- change multiple entry and start_balances
- `balances` and `--using`
- write to and read from Excel file

```bash
abacus entry --dr cash --cr equity --amount 1500 --title "Pay in shareholder capital" --push store.json
abacus dump --store store.json --to-excel-file store.xlsx
abacus read --from-excel-file store_fix.xlsx > store_fix.json
```

Example with `init`:

```bash
mkdir demo & cd demo
abacus init .
abacus chart set --assets cash goods
abacus chart set --expenses cogs sga
abacus chart set --capital equity
abacus chart set --retained_earnings re
abacus chart set --income sales
abacus chart offset sales cashback discounts
abacus chart validate
abacus post cash equity 5000
abacus post goods cash 1000
abacus post --entry cash sales 375 \
            --entry goods cogs 250 \
            --entry cashback cash 25 \
            --title "Sale of goods"
abacus post sga cash 40
abacus close
abacus name sga "Selling, general and adm.expenses"
abacus name cogs "Cost of goods sold"
abacus name re "Retained earnings"
abacus report --income-statement
abacus report --balance-sheet
abacus balances --output end_balances.json
```
