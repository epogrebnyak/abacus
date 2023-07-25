bx erase --chart
bx chart add--asset cash || exit /b
bx chart add--asset ar --title "Accounts receivable" || exit /b
bx chart offset ar bad_debt || exit /b
bx chart title bad_debt "Allowance for bad debts" || exit /b
bx chart add--asset goods --title "Inventory" || exit /b
bx chart add--expense cogs --title "Cost of goods sold" || exit /b 
bx chart add--expense sga --title "Selling expenses" || exit /b
bx chart add--capital equity || exit /b
bx chart add--liability ap --title "Accounts payable" || exit /b
bx chart add--retained-earnings re || exit /b
bx chart add--income sales || exit /b
bx chart offset sales discounts voids || exit /b
bx chart show || exit /b
bx chart show --json || exit /b