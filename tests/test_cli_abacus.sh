abacus --help
abacus chart unlink --yes
abacus chart init
abacus chart add asset:cash 
abacus chart add asset:goods
abacus chart add capital:equity
abacus chart set --retained-earnings-account re
abacus ledger unlink --yes
abacus ledger init
# bx ledger erase --force
# bx chart erase --force
# bx chart init
# bx chart add --asset cash 
# bx chart add --asset goods
# bx chart add --capital equity 
# bx chart set --retained-earnings re
# bx chart alias --operation capitalize --debit cash --credit equity
# bx ledger init
# bx ledger post operation capitalize 501 
# bx ledger post operation capitalize 499 --title "Second equity installment" 
# bx ledger post entry --debit goods --credit cash --amount 700 
# bx ledger post entry --debit goods --credit cash --amount 100 --title "More purchases"
# bx account cash
# bx assert cash 200
# bx assert equity 1000
# bx assert goods 800 
# bx balances --nonzero