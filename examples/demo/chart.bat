bx erase --chart
bx chart set --asset cash || exit /b
bx chart set --asset ar --title "Accounts receivable" || exit /b
bx chart offset ar bad_debt || exit /b
bx chart title bad_debt "Allowance for bad debts" || exit /b
bx chart set --asset goods --title "Inventory" || exit /b
bx chart set --expense cogs --title "Cost of goods sold" || exit /b 
bx chart set --expense sga --title "Selling expenses" || exit /b
bx chart set --capital equity || exit /b
bx chart set --liability ap --title "Accounts payable" || exit /b
bx chart set --retained-earnings re || exit /b
bx chart set --income sales || exit /b
bx chart offset sales discounts voids || exit /b
bx chart show || exit /b
bx chart show --json || exit /b