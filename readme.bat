abacus init
abacus add asset:cash,paper
abacus add capital:equity
abacus add income:sales contra:sales:refunds
abacus add expense:cogs,salaries
abacus post cash     sales 2675 --title="Sell paper for cash"
abacus post refunds  cash   375 --title="Client refund"
abacus post cogs     paper 2000 --title="Register cost of sales"
abacus post salaries cash   500 --title="Pay salaries"
abacus close
abacus report --all


