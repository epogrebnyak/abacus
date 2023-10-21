ex unlink chart --yes
ex unlink ledger --yes
ex init
ex add asset:ar --title "Accounts receivable" 
ex add liability:ap --title "Accounts payable"
ex add expense:ads --title "Advertising"
ex post --debit asset:cash               --credit capital:equity --amount 11000
ex post --debit expense:rent             --credit cash           --amount 800
ex post --debit asset:equipment          --credit ap             --amount 3000
ex post --debit cash                     --credit income:sales   --amount 1500
ex post --debit cash                     --credit liability:note --amount 700
ex post --debit ar                       --credit sales          --amount 2000
ex post --debit expense:salaries         --credit cash           --amount 500
ex post --debit expense:utilities        --credit cash           --amount 300
ex post --debit expense:ads              --credit cash           --amount 100
ex post --debit contra:equity:withdrawal --credit cash           --amount 1000
ex report trial-balance
ex close
ex report balance-sheet --rich
ex report income-statement --rich
ex report balance-sheet
ex report income-statement
ex report balance-sheet --json
ex report income-statement --json
ex account re --assert-balance 200