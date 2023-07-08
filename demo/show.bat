bx show report --income-statement --json || exit /b
bx show report --income-statement || exit /b
bx show report --balance-sheet --json || exit /b
bx show report --balance-sheet || exit /b
bx show balances --all --json || exit /b
bx show balances --all || exit /b
bx show balances --json || exit /b
bx show balances || exit /b 
bx show account cash || exit /b
bx show account goods || exit /b
bx show account sales || exit /b
bx assert sales 0 || exit /b
bx show account voids || exit /b
bx assert voids 0 || exit /b
bx show account discounts || exit /b
bx assert discounts 0 || exit /b
bx show account cogs || exit /b
bx show account sga || exit /b
bx show account re || exit /b
bx assert re 32 || exit /b

