bx init --force
bx chart set --assets cash goods
bx chart set --equity equity
bx chart set --retained-earnings re
bx ledger start
bx ledger post --debit cash --credit equity --amount 1000
bx ledger post --debit goods --credit cash --amount 800
bx show balances
bx assert equity 1000
bx assert cash 200
bx assert goods 800