# https://alqashi.com/book/Book50.pdf (pages)
abacus init
# TODO
cx post --debit asset:cash               --credit capital:equity     --amount 100_000
cx post --debit asset:equipment          --credit liability:notes    --amount  50_000
cx post --debit cash                     --credit liability:unearned --amount  12_000
cx name unearned "Unearned service revenue"
cx post --debit expense:rent             --credit cash               --amount   9_000
cx post --debit asset:prepaid_insurance  --credit cash               --amount   6_000
cx post --debit asset:supplies           --credit liability:ap       --amount  25_000
cx name ap "Accounts payable"
cx post --debit contra:equity:dividend   --credit cash               --amount   5_000
cx post --debit expense:salaries         --credit cash               --amount  40_000
cx post --debit cash                     --credit income:sales       --amount  28_000
cx post --debit asset:ar                 --credit sales              --amount  72_000
cx name ar "Accounts receivable"
cx report --trial-balance