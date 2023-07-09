bx erase --ledger 
bx ledger start --dry-run || exit /b
bx ledger start || exit /b
echo {"cash": 70, "goods": 30, "equity": 100} > start.json 
bx ledger start --file start.json --dry-run || exit /b
bx ledger start --file start.json || exit /b
del start.json
bx assert cash 70 || exit /b
bx assert goods 30 || exit /b
bx assert equity 100 || exit /b
bx post operation invoice 99 cost 25 || exit /b
bx post entry --debit voids --credit ar --amount 10 || exit /b
bx post entry -t "Discount to buyer" --debit discounts --credit ar --amount 8 || exit /b
bx post entry --debit cash --credit ar --amount 50 || exit /b
bx post entry --debit sga --credit ap --amount 24 || exit /b
bx post entry --debit ap --credit cash --amount 12 || exit /b
bx ledger close || exit /b
bx ledger list --start --json || exit /b
bx ledger list --business --json || exit /b
bx ledger list --adjust --json || exit /b
bx ledger list --close --json || exit /b
bx ledger list --after-close --json || exit /b
