abacus init
abacus add asset:cash,inv
abacus add capital:equity
abacus add income:sales expense:cogs,sga
abacus name inv "Inventory"
abacus name cogs "Cost of goods sold"
abacus name sga "Selling expenses"

abacus post cash equity 5000 --title "Shareholder investment"
abacus post  inv   cash 4000 --title "Purchased merchandise"
abacus post cash  sales 4800 --title "Sold merchandise"
abacus post cogs    inv 4000 --title "Registered cost of sales"
abacus post  sga   cash  500 --title "Paid sales representative"
abacus close

abacus report --balance-sheet
abacus report --income-statement

abacus add contra:sales:refunds
abacus post refunds cash 120 --title "Client refund"

abacus report --trial-balance

abacus report --account-balances
abacus report --account-balances > balances.json
# in next project
abacus load balances.json

abacus --help
abacus extra --help
