abacus inspect cash
abacus inspect cash --assert-balance 550
abacus inspect ar --assert-balance 450
abacus inspect equity --assert-balance 0 || echo "Captured planned failure."
