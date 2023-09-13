bx ledger erase --force
bx chart erase --force
bx chart init
bx chart add --asset cash 
bx chart add --asset goods
bx chart add --capital equity 
bx chart set --retained-earnings re
bx chart alias --operation capitalize --debit cash --credit equity
bx ledger init
bx ledger post --operation capitalize 500 
bx ledger post --operation capitalize 500 --title "Second capital installment" 
bx ledger post --debit goods --credit cash --amount 700 
bx ledger post --debit goods --credit cash --amount 100 --title "More purchases"
bx account equity --assert 1000
bx account cash --assert 200
bx account goods --assert 800 
bx balances --nonzero