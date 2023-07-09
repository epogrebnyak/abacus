bx erase --chart
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

bx erase --ledger
bx ledger start
bx post entry --debit cash      --credit equity --amount 1000
bx post entry --debit goods     --credit cash   --amount 800
bx post entry --debit ar        --credit sales  --amount 465
bx post entry --debit discounts --credit ar     --amount 65
bx post entry --debit cogs      --credit goods  --amount 200
bx post entry --debit sga       --credit cash   --amount 100
bx post entry --debit cash      --credit ar     --amount 360
bx ledger close
bx post entry --debit re --credit dividend_due --amount 50 --after-close

bx report --balance-sheet
bx report --income-statement

bx account cash
bx account ar
bx account goods
bx account sales
bx accounts

bx accounts --json > end_balances.json

bx assert cash 460
