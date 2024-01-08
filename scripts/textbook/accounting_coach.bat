abacus init
abacus add asset:cash,vehicles,prepaid_insurance
abacus add asset:ar --title "Accounts receivable"
abacus add liability:ap --title "Accounts payable"
abacus add income:services
abacus add expense:agency --title "Temporary help agency"
abacus add capital:common_stock
abacus post cash common_stock 20000 --title "1. Owner's investment"
abacus post vehicles cash 14000 --title "2. Purchased vehicle"
abacus post prepaid_insurance cash 1200 --title "3. Bought insurance"
abacus post cash services 10 --title "4. Accepted cash for provided services"
abacus post ar services 250 --title "5. Provided services on account"
abacus post agency ap 80 --title "6. Purchased services on account"
abacus close
abacus report --all