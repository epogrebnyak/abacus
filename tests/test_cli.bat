bx erase --chart || exit /b
bx erase --ledger || exit /b
bx chart add --asset cash || exit /b
bx chart add --asset goods || exit /b
bx chart add --capital equity || exit /b
bx chart add --retained-earnings re || exit /b
bx operation set capitalize --debit cash --credit equity
bx ledger start || exit /b
bx post operation capitalize 500 || exit /b
bx post operation -t "Second capital installment" capitalize 500 || exit /b
bx post entry --debit goods --credit cash --amount 700 || exit /b
bx post entry --title "More purchases" --debit goods --credit cash --amount 100 || exit /b
bx assert equity 1000 || exit /b
bx assert cash 200 || exit /b
bx assert goods 800 || exit /b
bx accounts --json || exit /b
