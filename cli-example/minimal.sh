bx chart set --asset cash
bx chart set --asset ar --title "Accounts receivable"
bx chart set --asset goods --title "Inventory (good for sale)"
bx chart set --capital equity
bx chart set --retained-earnings re
bx chart set --liability dividend_due
bx chart set --income sales
bx chart set --expense cogs --title "Cost of sales"
bx chart set --expense sga --title "Selling expenses"
bx chart offset sales discounts
bx chart show

bx ledger start
bx ledger post --debit cash      --credit equity --amount 1000
bx ledger post --debit goods     --credit cash   --amount 800
bx ledger post --debit ar        --credit sales  --amount 465
bx ledger post --debit discounts --credit ar     --amount 65
bx ledger post --debit cogs      --credit goods  --amount 200
bx ledger post --debit sga       --credit cash   --amount 100
bx ledger post --debit cash      --credit ar     --amount 360
bx ledger close
bx ledger post --debit re --credit dividend_due --amount 50 --after-close

bx show report --balance-sheet
bx show report --income-statement
bx show balances

bx show balances --json > end_balances.json

bx show account cash
bx show account ar
bx show account goods
bx show account sales

bx assert cash 460
