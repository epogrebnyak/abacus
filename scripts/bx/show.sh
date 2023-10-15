bx account cash
bx assert cash 550
bx assert cash 551 || echo "Captured failure."
bx balances 
bx balances --nonzero
bx balances --nonzero > balances.json
