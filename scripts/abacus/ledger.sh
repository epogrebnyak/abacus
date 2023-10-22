abacus ledger unlink --yes
echo {\"cash\": 550, \"ar\": 450, \"goods\": 50, \"equity\": 1000, \"re\": 50} > balances.json
abacus ledger init --file balances.json
abacus ledger show
abacus ledger unlink --yes
abacus ledger init
abacus ledger post --debit cash --credit equity --amount 1000
abacus ledger post --debit goods --credit cash --amount 700
#abacus ledger post operation invoice 850 cost 650
abacus ledger post --debit ar --credit sales --amount 850
abacus ledger post --debit cogs --credit goods --amount 650
abacus ledger post --debit cash --credit ar --amount 400
abacus ledger post --debit sga --credit cash --amount 150
abacus ledger close
abacus ledger show

