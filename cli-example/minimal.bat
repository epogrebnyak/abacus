call bx chart set --asset cash || exit /b
call bx chart set --asset ar --title "Accounts receivable" || exit /b
call bx chart set --asset goods --title "Inventory (good for sale)" || exit /b
call bx chart set --capital equity || exit /b
call bx chart set --retained-earnings re || exit /b
call bx chart set --liability dividend_due || exit /b
call bx chart set --income sales || exit /b
call bx chart set --expense cogs --title "Cost of sales" || exit /b
call bx chart set --expense sga --title "Selling expenses" || exit /b
call bx chart offset sales discounts || exit /b
call bx chart show || exit /b


call bx ledger start || exit /b
call bx ledger post --debit cash      --credit equity --amount 1000 || exit /b
call bx ledger post --debit goods     --credit cash   --amount 800 || exit /b
call bx ledger post --debit ar        --credit sales  --amount 465 || exit /b
call bx ledger post --debit discounts --credit ar     --amount 65 || exit /b
call bx ledger post --debit cogs      --credit goods  --amount 200 || exit /b
call bx ledger post --debit sga       --credit cash   --amount 100 || exit /b
call bx ledger post --debit cash      --credit ar     --amount 360 || exit /b
call bx ledger close || exit /b
call bx ledger post --debit re --credit dividend_due --amount 50 --after-close || exit /b


call bx show report --balance-sheet || exit /b
call bx show report --income-statement || exit /b
call bx show balances || exit /b


call bx show balances --json > end_balances.json || exit /b


call bx show account cash || exit /b
call bx show account ar || exit /b
call bx show account goods || exit /b
call bx show account sales || exit /b


call bx assert cash 460 || exit /b
