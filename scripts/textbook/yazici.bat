bx unlink --yes
bx init
bx chart add --asset cash equipment prepaid_insurance supplies
bx chart add asset:ar --title "Accounts receivable"     
bx chart add capital:equity contra:equity:dividend
bx chart add liability:notes 
bx chart add liability:unearned --title "Unearned service revenue"
bx chart add liability:ap --title "Accounts payable"
bx chart add expense:rent,salaries
bx chart add income:sales
bx post --entry cash equity 100_000
bx post --entry equipment notes 50_000
bx post --entry cash unearned 12_000
bx post --entry rent cash 9_000
bx post --entry prepaid_insurance cash 6_000
bx post --entry supplies ap 25_000
bx post --entry dividend cash 5_000
bx post --entry salaries cash 40_000
bx post --entry cash sales 28_000
bx post --entry ar sales 72_000
bx report --trial-balance