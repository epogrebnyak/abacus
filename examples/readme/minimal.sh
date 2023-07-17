pip install -U abacus-py
mkdir try_abacus && cd try_abacus
bx chart set --asset cash
bx chart set --asset ar --title "Accounts receivable"
bx chart set --asset goods --title "Inventory (goods for resale)"
bx chart set --capital equity
bx chart set --retained-earnings re
bx chart set --income sales
bx chart offset --account sales --contra-accounts discounts
bx chart set --expense cogs --title "Cost of goods sold"
bx chart set --expense sga --title "Selling, general and adm. expenses"
bx chart show
bx ledger start
bx post entry --title "Initial investment"     --debit cash  --credit equity --amount 5000
bx post entry --title "Acquire goods for cash" --debit goods --credit cash   --amount 4000
bx post entry --title "Register cost of sales" --debit cogs  --credit goods  --amount 2700
bx post entry --title "Issue invoice"          --debit ar    --credit sales  --amount 3900
bx post entry --title "Provide discount"       --debit discounts --credit ar --amount  400
bx post entry --title "Accept payment"         --debit cash  --credit ar     --amount 2000
bx post entry --title "Paid sales team salary" --debit sga   --credit cash   --amount  300
bx ledger close
bx report --balance-sheet
bx report --income-statement
