abacus extra unlink --yes 
abacus init
abacus add asset:cash, equipment 
abacus add capital:equity contra:equity:withdrawal 
abacus add expense:rent liability:note 
abacus add asset:ar --title "Accounts receivable"
abacus add asset:ap --title "Accounts payable"
abacus add income:sales expense:salaries,utilities
abacus add expense:ads --title "Advertising"
abacus post cash       equity  11000
@REM abacus post rent       cash      800
@REM abacus post equipment  ap       3000
@REM abacus post cash       sales    1500
@REM abacus post cash       note      700
@REM abacus post ar         sales    2000
@REM abacus post salaries   cash      500
@REM abacus post utilities  cash      300
@REM abacus post ads        cash      100
@REM abacus post withdrawal cash     1000
abacus report --trial-balance
abacus close
abacus report --balance-sheet
abacus report --income-statement
