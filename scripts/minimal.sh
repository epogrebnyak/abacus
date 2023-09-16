bx chart init
bx chart add --asset cash
bx chart add --asset ar --title "Accounts receivable"
bx chart add --asset goods --title "Inventory (goods for resale)"
bx chart add --capital equity
bx chart add --income sales
bx chart offset sales discounts
bx chart add --expense cogs --title "Cost of goods sold"
bx chart add --expense sga --title "Selling, general and adm. expenses"
bx chart alias --operation invoice --debit sales --credit ar
bx chart alias --operation cost --debit cogs --credit goods
bx chart show

bx ledger init
bx ledger post --debit cash  --credit equity --amount 5000 --title "Initial investment"
bx ledger post --debit goods --credit cash   --amount 4000 --title "Acquire goods for cash"
bx ledger post --operation invoice 3900 cost 2700          --title "Issue invoice and register sales"
bx ledger post --debit discounts --credit ar --amount  400 --title "Provide discount"
bx ledger post --debit cash  --credit ar     --amount 2000 --title "Accept payment"
bx ledger post --debit sga   --credit cash   --amount  300 --title "Reimburse sales team"
bx ledger close

bx report --trial-balance
bx report --balance-sheet
bx report --income-statement
