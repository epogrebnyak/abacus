bx unlink --yes
bx init
bx post --entry asset:cash capital:common_stock 20000 --title "Initial investment"
bx report --balance-sheet
bx show balances --nonzero > start.json
bx ledger unlink --yes
bx ledger init
bx assert cash 0
bx post --starting-balances-file start.json
bx assert cash 20000 
bx post --entry cash income:sales 500
bx close 
bx assert retained_earnings 500