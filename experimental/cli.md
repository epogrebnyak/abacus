CLI examples ()

### Minimal example

- Chart of accounts has just 7 accounts.
- Firm created, acquires and sells some goods.
- Cash basis, no payables/receivables.
- Print income statement and balance sheet.
- Save period end account balances to file.

```bash
mkdir demo & cd demo
abacus init .
abacus chart set --assets cash,goods \
                 --expenses cogs,sga \
                 --capital equity \
                 --retained_earnings re \
                 --income sales
abacus post cash equity 5000
abacus post goods cash 1000
abacus post --entry cash sales 350 \
            --entry goods cogs 250
abacus post sga cash 40
abacus close --all
abacus name sga "Selling, general and adm.expenses"
abacus name cogs "Cost of goods sold"
abacus name re "Retained earnings"
abacus report --income-statement
abacus report --balance-sheet
abacus balances --output end_balances.json
```

<details>
  <summary>Click to reveal extended script</summary>
  
```bash
# Start project
mkdir books_2023 & cd books_2023  
abacus init .

# Create chart of accounts

abacus chart set --assets cash,prepaid_rent,goods_for_sale \
 --expenses overhead,cogs,sga,rent \
 --capital shareholder_equity \
 --retained_earnings retained_earnings \
 --income sales

# two ways to add contra accounts

# 1. add ppe account

abacus chart add --assets ppe --contra-accounts depreciation --resulting-name net_ppe

# 2. ppe account must already exist in chart

abacus chart offset ppe --resulting-name net_ppe --contra-accounts depreciation
abacus chart add --contra-accounts discount cashback --link sales --create net_sales
abacus chart add --liabilities loans dividend_due
abacus chart add --expenses interest

# Add entries

abacus post cash shareholder_equity 2000 -t "Pay in shareholder capital"
abacus post prepaid_rent cash 240 -t "Prepay property rent (1 year)"
abacus post cash sales 880 -t "Service revenue (contract #306-2)"
abacus post sales discount 30 -t "Client discount (contract #306-2)"
abacus post sales cashback 50 -t "Client cashback (contract #306-2)"
abacus post sga cash 250 -t "Selling expenses"

# Close accounting period

abacus show trial-balance
abacus adjust prepaid_rent rent 60 -t "Accrue expenses (3 months)"
abacus close --all
abacus post-close retained_earnings dividend_due 200 -t "Announced dividend"

# Show reports

abacus add name sga "Selling, general and adm.expenses"
abacus add name cogs "Cost of goods sold"
abacus report --income-statement
abacus show report --balance-sheet
abacus status
abacus --version
abacus --help
abacus --dir . --filename abacus.toml show config

````

### `init` command

`abacus init .` is equivalent to the following:

```bash
touch ./abacus.toml
abacus --dir . create chart --output chart.json
abacus --dir . create store --output entries.json
abacus --dir . create names --output names.json
````

### minimal command group

`jaba` is a minimal subset of `abacus` commands without configuration file:

- zero config (no `abacus.toml`)
- no `rename`
- no `init`

```bash
jaba chart new --output chart.json
jaba chart add --assets <names> --chart chart.json
jaba chart add --expenses <names> --chart chart.json
jaba chart add --capital <names> --chart chart.json
jaba chart add --liabilities <names> --chart chart.json
jaba chart add --income <names> --chart chart.json
jaba chart offset <name> --contra-accounts <names> --resulting-name <new_name> --chart chart.json
jaba store new [--start-balances start_balances.json] --output entries.json
jaba entry new --dr dr_account --cr cr_account --amount amount [--chart chart.json]
jaba entry add --dr dr_account --cr cr_account --amount amount --store entries.json [--chart chart.json]
jaba store list ([--entry] [--rename] [--mark]) | [--all] --store entries.json
jaba report -t --chart chart.json --store entries.json > trial_balance.json
jaba close --contra-income --contra-expenses --chart chart.json --store entries.json
jaba close --income --expenses --isa --chart chart.json --store entries.json
jaba report -i --chart chart.json --store entries.json > income_statement.json
jaba report -b --chart chart.json --store entries.json > balance_sheet.json
jaba report -e --chart chart.json --store entries.json > end_balances.json
```

</details>
