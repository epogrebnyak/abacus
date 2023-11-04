abacus account show-balances 
abacus account show-balances --nonzero
abacus account show cash
abacus account assert --balance ar 450 --balance cash 550 
abacus account assert --balance equity -1 || echo "Captured planned failure."


