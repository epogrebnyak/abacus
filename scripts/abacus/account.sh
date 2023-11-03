abacus account show-balances 
abacus account show-balances --nonzero
abacus account show cash
abacus account assert cash 550
abacus account assert ar 450
abacus account assert equity -1 || echo "Captured planned failure."


