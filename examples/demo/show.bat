bx report --income-statement --json || exit /b
bx report --income-statement || exit /b
bx report --balance-sheet --json || exit /b
bx report --balance-sheet || exit /b
bx accounts --all --json || exit /b
bx accounts --all || exit /b
bx accounts --json || exit /b
bx accounts || exit /b 
bx account cash || exit /b
bx account goods || exit /b
bx account sales || exit /b
bx assert sales 0 || exit /b
bx account voids || exit /b
bx assert voids 0 || exit /b
bx account discounts || exit /b
bx assert discounts 0 || exit /b
bx account cogs || exit /b
bx account sga || exit /b
bx account re || exit /b
bx assert re 32 || exit /b

