abacus extra unlink --yes
abacus init
abacus post asset:cash capital:common_stock 20000 --title "1. Owner's investment"
abacus post asset:vehicles cash             14000 --title "2. Purchased vehicle"
abacus post asset:prepaid_insurance cash     1200 --title "3. Bought insurance"
abacus post cash income:services               10 --title "4. Accepted cash for provided services"
abacus post asset:ar services                 250 --title "5. Provided services on account"
abacus post expense:agency liability:ap        80 --title "6. Purchased services on account"
abacus close
abacus name ar "Accounts receivable"
abacus name ap "Accounts payable"
abacus name agency "Temporary help agency"
abacus report --all