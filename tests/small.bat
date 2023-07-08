bx erase --chart --entries || exit /b
bx chart set --asset cash || exit /b
bx chart set --asset goods || exit /b
bx chart set --capital equity || exit /b
bx chart set --retained-earnings re || exit /b
bx operation set capitalize --debit cash --credit equity
bx ledger start || exit /b
bx post capitalize 1000 || exit /b
bx post entry --debit goods --credit cash --amount 800 || exit /b
bx assert equity 1000 || exit /b
bx assert cash 200 || exit /b
bx assert goods 800 || exit /b
bx show balances --json || exit /b
