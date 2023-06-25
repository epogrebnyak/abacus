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
bx name re --title "Retained earnings" || exit /b
bx name ar --title "Accounts receivable" || exit /b
bx name ap --title "Accounts payable" || exit /b
bx name ppe --title "Fixed assets" || exit /b
bx name goods --title "Inventory (goods for sale)" || exit /b
bx name cogs --title "Cost of goods sold" || exit /b
bx name sga --title "Selling, general and adm. expenses" || exit /b
bx ledger start --empty --dry-run || exit /b
bx ledger start --empty || exit /b
echo {"cash": 70, "goods": 30, "equity": 100} > start.json 
bx ledger start --file start.json --dry-run || exit /b
bx ledger start --file start.json || exit /b
bx ledger post --debit ar --credit sales --amount 99 || exit /b
bx ledger post --debit sales --credit refunds --amount 10 || exit /b
bx ledger post --debit sales --credit discounts --amount 8 || exit /b
bx ledger post cogs goods 25 || exit /b
bx ledger post sga ap 24 || exit /b
bx ledger post ap cash 12 || exit /b
bx ledger close || exit /b
bx ledger show --start --json 
bx ledger show --business --json || exit /b
bx ledger show --adjust --json || exit /b
bx ledger show --close --json || exit /b
bx ledger show --post-close --json || exit /b
bx report --income-statement --json || exit /b
bx report --income-statement || exit /b
bx report --balance-sheet --json || exit /b
bx report --balance-sheet || exit /b
bx balances --all --json || exit /b
bx balances --all || exit /b
bx balances --nonzero --json || exit /b
bx balances --nonzero || exit /b 
bx account cash || exit /b
bx account sales || exit /b
bx account refunds || exit /b
bx account re || exit /b
bx account re --assert-balance 50 || exit /b

