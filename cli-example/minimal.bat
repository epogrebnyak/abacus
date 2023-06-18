call jaba chart chart.json unlink
call jaba chart chart.json touch
call jaba chart chart.json set --assets cash ar goods ppe
call jaba chart chart.json set --capital equity
call jaba chart chart.json set --retained-earnings re
call jaba chart chart.json set --liabilities ap dividend_due
call jaba chart chart.json set --income sales
call jaba chart chart.json set --expenses cogs sga
call jaba chart chart.json offset ppe depreciation
call jaba chart chart.json offset sales discounts cashback
call jaba chart chart.json list --validate

call jaba ledger store.json init chart.json
call jaba ledger store.json post --dr cash --cr equity --amount 1000
call jaba ledger store.json post goods cash 300
call jaba ledger store.json post cogs goods 250
call jaba ledger store.json post ar sales 440
call jaba ledger store.json post discounts ar 41
call jaba ledger store.json post cash ar 150
call jaba ledger store.json post sga cash 69
call jaba ledger store.json close
call jaba ledger store.json list --business
call jaba ledger store.json list --close

call jaba report store.json --balance-sheet
call jaba report store.json --income-statement

call jaba balances store.json account cash

call jaba balances store.json account cash --assert 781
call jaba balances store.json account ar --assert 241
call jaba balances store.json account goods --assert 50
call jaba balances store.json account equity --assert 1000
call jaba balances store.json account re --assert 80

call jaba balances store.json list --skip-zero

call jaba balances store.json list --skip-zero --json > end_balances.json

