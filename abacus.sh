abacus chart unlink --yes
abacus chart init
abacus chart add-many asset:cash asset:goods capital:equity expense:cogs expense:sga income:sales liabilities:ap 
abacus chart add contra:sales:refunds
abacus chart add asset:ar --title "Accounts receivable" 
abacus chart name cogs --title "Cost of goods sold"
abacus chart name sga --title "Selling and similar expenses"
abacus chart name ap --title "Accounts payable"
abacus chart show --json
abacus chart --help
abacus ledger unlink --yes
# works without init as well
abacus ledger init
abacus ledger post --debit asset:cash               --credit capital:equity --amount 11000
abacus ledger post --debit expense:rent             --credit cash           --amount 800
abacus ledger post --debit asset:equipment          --credit ap             --amount 3000
abacus ledger post --debit cash                     --credit income:sales   --amount 1500
abacus ledger post --debit cash                     --credit liability:note --amount 700
abacus ledger post --debit ar                       --credit sales          --amount 2000
abacus ledger post --debit expense:salaries         --credit cash           --amount 500
abacus ledger post --debit expense:utilities        --credit cash           --amount 300
abacus ledger post --debit expense:ads              --credit cash           --amount 100
abacus ledger post --debit contra:equity:withdrawal --credit cash           --amount 1000
abacus ledger close
abacus ledger show
abacus ledger --help
abacus report trial-balance
