bx ledger erase --force
echo {\"cash\": 550, \"ar\": 450, \"goods\": 50, \"equity\": 1000, \"re\": 50} > balances.json
bx ledger init balances.json
bx ledger show
bx ledger erase --force
bx ledger init
bx ledger post entry --debit cash --credit equity --amount 1000
bx ledger post entry --debit goods --credit cash --amount 700
bx ledger post operation invoice 850 cost 650
bx ledger post entry --debit cash --credit ar --amount 400
bx ledger post entry --debit sga --credit cash --amount 150
bx ledger close
bx ledger show
