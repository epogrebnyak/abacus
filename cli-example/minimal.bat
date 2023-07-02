call bx init --force || exit /b
call bx chart set --assets cash ar goods || exit /b
call bx chart set --equity equity || exit /b
call bx chart set --retained-earnings re || exit /b
call bx chart set --liabilities dividend_due || exit /b
call bx chart set --income sales || exit /b
call bx chart set --expenses cogs sga || exit /b
call bx chart offset sales --contra-accounts discounts || exit /b
call bx chart list || exit /b


call bx ledger start || exit /b
call bx ledger post --debit cash --credit equity --amount 1000 || exit /b
call bx ledger post --debit goods --credit cash --amount 800 || exit /b
call bx ledger post --debit ar --credit sales --amount 965 || exit /b
call bx ledger post --debit discounts --credit ar --amount 30 || exit /b
call bx ledger post --debit cogs --credit goods --amount 600 || exit /b
call bx ledger post --debit sga --credit cash --amount 185 || exit /b
call bx ledger post --debit cash --credit ar --amount 725 || exit /b
call bx ledger close || exit /b
call bx ledger post --debit re --credit dividend_due --amount 60 --after-close || exit /b


call bx show report --balance-sheet || exit /b
call bx show report --income-statement || exit /b
call bx show balances || exit /b


call bx show balances --json > end_balances.json || exit /b


call bx show account cash || exit /b
call bx show account ar || exit /b
call bx show account goods || exit /b
call bx show account sales || exit /b


call bx assert cash 740 || exit /b
