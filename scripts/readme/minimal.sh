abacus --help
cx --help

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

cat chart.json

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

cat entries.linejson

abacus report trial-balance
abacus report balance-sheet
abacus report income-statement

abacus account show sales

abacus account assert --balance cash 3000 --balance ar 850 --balance goods 1000

abacus account show-balances --nonzero
