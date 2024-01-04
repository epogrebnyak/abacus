abacus --help
abacus chart unlink --yes
abacus chart init
abacus chart add --asset cash 
abacus chart add --asset goods
abacus chart add --capital equity
abacus chart set --retained-earnings-account re
abacus ledger unlink --yes
abacus ledger init
abacus ledger post --debit cash --credit equity --amount 501
abacus-extra alias add --operation capitalize --debit cash --credit equity
abacus-extra alias post --operation capitalize 499
abacus ledger post --debit goods --credit cash --amount 700 
abacus ledger post-compound --debit expense:cogs 600 --credit goods 600 
abacus ledger post-compound --credit income:sales 1000 --debit cash 800 --debit asset:ar 200 
abacus ledger show
