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

```bash
account -m cash "Cash"
account -ac inv "Inventories"
account -ac ar "Accounts receivable" 
account -an ppe "Property, plant, equipment" 
account -an gw "Goodwill" 
account -e cos "Cost of sales"
account -e dc "Distribution costs"
account -e ae "Administrative expenses" 
account -e de "Depreciation expense"
account -с eq "Shareholder equity"
account -r re "Retained earnings"
account -l ap "Accounts payable"
account -i sales "Revenue"
account --contra sales discounts 

```

```bash
mkdir demo & cd demo
abacus init .
abacus save dwp.json
abacus chart --check
abacus chart --assets cash ar inv ppe
abacus chart --expenses cogs sga de 
abacus account -m cash 
abacus account -m bank "Bank account"
abacus account -a ar "Accounts receivable" 
abacus account -a ppe "Property, plant, equipment" 
abacus account -e cos "Cost of sales" 
abacus account -e de "Depreciation expense" 
abacus chart --capital equity
abacus chart --re re
abacus chart --income sales
abacus chart --liabilities ap loan
abacus chart --offset sales cashback
abacus chart --offset ppe depr
abacus post cash equity 5000 -t "Paid in capital"
abacus post -e goods ap 1000  -e ap cash 300 -t "Bought goods on credit"
abacus post -e cash sales 375 \
            -e goods cogs 250 \
            -e cashback cash 25 -t "Sold goods"
abacus post sga cash 40 -t "Selling expenses"
abacus close
abacus name sga "Selling, general and adm.expenses"
abacus name cogs "Cost of goods sold"
abacus name re "Retained earnings"
abacus report --income-statement
abacus report --balance-sheet
abacus report --trial-balance --output end_balances.json
```
