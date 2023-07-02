call bx init --force || exit /b
call bx chart set --assets cash ar goods || exit /b
call bx chart set --equity equity || exit /b
call bx chart set --retained-earnings re || exit /b
call bx chart set --liabilities ap || exit /b
call bx chart set --income sales || exit /b
call bx chart set --expenses cogs sga || exit /b
call bx chart offset sales --contra-accounts discounts cashback || exit /b
call bx chart list || exit /b


call bx ledger start || exit /b
call bx ledger post cash equity 1000 || exit /b
call bx ledger post goods cash 300 || exit /b
call bx ledger post cogs goods 250 || exit /b
call bx ledger post ar sales 440 || exit /b
call bx ledger post discounts ar 41 || exit /b
call bx ledger post cash ar 150 || exit /b
call bx ledger post sga cash 69 || exit /b
call bx ledger close || exit /b
call bx ledger list --business || exit /b
call bx ledger list --close || exit /b


call bx show report --balance-sheet || exit /b
call bx show report --income-statement || exit /b
call bx show balances || exit /b


call bx show balances --json > end_balances.json || exit /b


call bx show account cash || exit /b
call bx show account ar || exit /b
call bx show account goods || exit /b
call bx show account equity || exit /b
call bx show account re || exit /b


call bx assert cash 781 || exit /b
call bx assert ar 249 || exit /b
call bx assert goods 50 || exit /b
call bx assert equity 1000 || exit /b
call bx assert re 80 || exit /b
