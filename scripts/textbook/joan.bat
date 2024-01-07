abacus extra unlink --yes 
abacus init
abacus add asset:cash asset:equipment 
abacus add capital:equity contra:equity:withdrawal 
abacus add expense:rent liability:note 
abacus add liability:ar --title "Accounts receivable"
abacus add asset:ap --title "Accounts payable"
abacus add income:sales expense:salaries,utilities
abacus add expense:ads --title "Advertising"
abacus post cash       equity  11000
abacus post rent       cash      800
abacus post equipment  ar       3000
abacus post cash       sales    1500
abacus post cash       note      700
abacus post ap         sales    2000
abacus post salaries   cash      500
abacus post utilities  cash      300
abacus post ads        cash      100
abacus post withdrawal cash     1000
abacus report --trial-balance
abacus close
abacus report --balance-sheet
abacus report --income-statement
abacus assert retained_earnings 1800 
