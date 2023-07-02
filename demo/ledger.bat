bx ledger start --dry-run || exit /b
bx ledger start || exit /b
echo {"cash": 70, "goods": 30, "equity": 100} > start.json 
bx ledger start --file start.json --dry-run || exit /b
bx ledger start --file start.json || exit /b
bx assert cash 70 || exit /b
bx assert goods 30 || exit /b
bx assert equity 100 || exit /b
bx ledger post --debit ar --credit sales --amount 99 || exit /b
bx ledger post --debit refunds --credit ar --amount 10 || exit /b
bx ledger post --debit discounts --credit ar --amount 8 || exit /b
bx ledger post cash ar 50 || exit /b
bx ledger post cogs goods 25 || exit /b
bx ledger post sga ap 24 || exit /b
bx ledger post ap cash 12 || exit /b
bx ledger close || exit /b
bx ledger list --start --json || exit /b
bx ledger list --business --json || exit /b
bx ledger list --adjust --json || exit /b
bx ledger list --close --json || exit /b
bx ledger list --post-close --json || exit /b
