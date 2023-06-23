bx init --force || exit /b
bx init
bx chart set --assets cash ar goods || exit /b 
bx chart set --equity equity || exit /b
bx chart set --retained-earnings re || exit /b
bx chart set --liabilities ap || exit /b
bx chart set --income sales || exit /b
bx chart set --expenses cogs sga || exit /b
bx chart offset sales --contra-accounts discounts refunds || exit /b
bx chart offset equity --contra-accounts treasury_stock || exit /b
bx chart show || exit /b
bx chart show --json || exit /b
bx ledger start --empty --dry-run || exit /b
bx ledger start --empty || exit /b
echo {"cash": 70, "goods": 30, "equity": 100} > start.json 
bx ledger start --file start.json --dry-run || exit /b
bx ledger start --file start.json || exit /b
bx ledger post --debit ar --credit sales --amount 99 || exit /b
bx ledger post --debit sales --credit refunds --amount 10 || exit /b
bx ledger post --debit sales --credit discounts --amount 9 || exit /b
bx ledger post cogs goods 25 || exit /b
bx ledger post sga ap 15 || exit /b
bx ledger post ap cash 10 || exit /b
bx ledger close || exit /b
bx report --income-statement --json || exit /b
bx report --income-statement || exit /b
bx report --balance-sheet --json || exit /b
bx report --balance-sheet || exit /b
bx balances --all --json
bx balances --all
bx balances --nonzero --json
bx balances --nonzero 
bx account re 
bx account re --assert-balance 59

