abacus extra unlink --yes
abacus init
abacus add asset:cash asset:equipment asset:prepaid_insurance asset:supplies
abacus add asset:ar --title "Accounts receivable"     
abacus add capital:equity contra:equity:dividend
abacus add liability:notes 
abacus add liability:unearned --title "Unearned service revenue"
abacus add liability:ap --title "Accounts payable"
abacus add expense:rent,salaries
abacus add income:sales
abacus post cash equity 100_000
abacus post equipment notes 50_000
abacus post cash unearned 12_000
abacus post rent cash 9_000
abacus post prepaid_insurance cash 6_000
abacus post supplies ap 25_000
abacus post dividend cash 5_000
abacus post salaries cash 40_000
abacus post cash sales 28_000
abacus post ar sales 72_000
abacus report --trial-balance