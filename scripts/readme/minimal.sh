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

bx ledger init
bx ledger post entry --debit cash  --credit equity --amount 5000 --title "Initial investment"
bx ledger post entry --debit goods --credit cash   --amount 3500 --title "Acquire goods for cash"
bx ledger post entry --debit prepaid_rent --credit cash --amount 1200 --title "Prepay rent"
bx ledger post operation invoice 4300 cost 2500 --title "Issue invoice and register sales"
bx ledger post entry --debit discounts --credit ar --amount  450 --title "Provide discount"
bx ledger post entry --debit cash  --credit ar     --amount 3000 --title "Accept payment"
bx ledger post entry --debit sga   --credit cash   --amount  300 --title "Reimburse sales team"
bx ledger post entry --debit sga --credit prepaid_rent --amount 800 --title "Expense 8 months of rent" --adjust
bx ledger close
bx ledger post entry --debit re --credit dividend_due --amount 150 --title "Accrue dividend" --after-close

bx report --trial-balance
bx report --balance-sheet
bx report --income-statement

bx account sales
bx assert cash 3000

bx balances --nonzero
