abacus report account cash
abacus report account cash --assert-balance 550
abacus report account ar --assert-balance 450
abacus report account equity --assert-balance 0 || echo "Captured planned failure."
