abacus init
abacus add asset:cash
abacus add asset:paper --title "Inventory"
abacus add capital:equity
abacus add income:sales contra:sales:refunds
abacus add expense:cogs --title "Cost of goods sold"
abacus add salaries
echo {"cash": 300, "paper": 2200, "equity": 2500} > starting_balances.json
abacus load starting_balances.json
abacus post cash     sales 2675 --title="Sell paper for cash"
abacus post refunds  cash   375 --title="Client refund"
abacus post cogs     paper 2000 --title="Register cost of sales"
abacus post salaries cash   500 --title="Pay salaries"
abacus close
abacus report --all

pip install abacus-py
