bx init --force
bx chart set --assets cash ar goods
bx chart set --equity equity
bx chart set --retained-earnings re
bx chart set --liabilities ap
bx chart set --income sales
bx chart set --expenses cogs sga
bx chart offset sales --contra-accounts discounts cashback
bx chart list

bx ledger start
bx ledger post cash equity 1000
bx ledger post goods cash 300
bx ledger post cogs goods 250
bx ledger post ar sales 440
bx ledger post discounts ar 41
bx ledger post cash ar 150
bx ledger post sga cash 69
bx ledger close
bx ledger list --business
bx ledger list --close

bx show report --balance-sheet
bx show report --income-statement
bx show balances

bx show balances --json > end_balances.json

bx show account cash
bx show account ar
bx show account goods
bx show account equity
bx show account re

bx assert cash 781
bx assert ar 249
bx assert goods 50
bx assert equity 1000
bx assert re 80
