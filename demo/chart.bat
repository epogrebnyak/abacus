bx init --force || exit /b
bx init
bx chart set --assets cash ar goods || exit /b 
bx chart set --assets cash ar goods || exit /b 
bx chart set --equity equity || exit /b
bx chart set --retained-earnings re || exit /b
bx chart set --liabilities ap || exit /b
bx chart set --income sales || exit /b
bx chart set --expenses cogs sga || exit /b
bx chart offset sales --contra-accounts discounts refunds || exit /b
bx chart offset equity --contra-accounts treasury_stock || exit /b
bx chart name re --title "Retained earnings" || exit /b
bx chart name ar --title "Accounts receivable" || exit /b
bx chart name ap --title "Accounts payable" || exit /b
bx chart name ppe --title "Fixed assets" || exit /b
bx chart name goods --title "Inventory (goods for sale)" || exit /b
bx chart name cogs --title "Cost of goods sold" || exit /b
bx chart name sga --title "Selling, general and adm. expenses" || exit /b
bx chart list || exit /b
bx chart list --json || exit /b
