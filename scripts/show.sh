bx account cash
bx account cash --assert 550
bx account cash --assert 551 || echo "Captured failure."
bx balances 
bx balances --nonzero
bx balances --nonzero > balances.json
