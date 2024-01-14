bx unlink --yes
bx init
bx chart add asset:cash asset:equipment 
bx chart add capital:equity contra:equity:withdrawal 
bx chart add expense:rent liability:note 
bx chart add liability:ar --title "Accounts receivable"
bx chart add asset:ap --title "Accounts payable"
bx chart add income:sales expense:salaries,utilities
bx chart add expense:ads --title "Advertising"
bx post --entry cash       equity  11000
bx post --entry  rent       cash      800
bx post --entry  equipment  ar       3000
bx post --entry  cash       sales    1500
bx post --entry  cash       note      700
bx post --entry  ap         sales    2000
bx post --entry  salaries   cash      500
bx post --entry utilities  cash      300
bx post --entry  ads        cash      100
bx post --entry  withdrawal cash     1000
bx report --trial-balance
bx close
bx report --balance-sheet
bx report --income-statement
bx assert retained_earnings 1800 
