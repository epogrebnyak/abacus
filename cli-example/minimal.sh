jaba chart chart.json unlink
jaba chart chart.json touch
jaba chart chart.json set --assets cash ar goods ppe
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba chart chart.json set --liabilities ap dividend_due
jaba chart chart.json set --income sales
jaba chart chart.json set --expenses cogs sga
jaba chart chart.json offset ppe depreciation
jaba chart chart.json offset sales discounts cashback
jaba chart chart.json list --validate

jaba ledger store.json init chart.json
jaba ledger store.json post --dr cash --cr equity --amount 1000
jaba ledger store.json post goods cash 300
jaba ledger store.json post cogs goods 250
jaba ledger store.json post ar sales 440
jaba ledger store.json post discounts ar 41
jaba ledger store.json post cash ar 150
jaba ledger store.json post sga cash 69
jaba ledger store.json close
jaba ledger store.json list --business
jaba ledger store.json list --close

jaba report store.json --balance-sheet
jaba report store.json --income-statement

jaba balances store.json account cash

jaba balances store.json account cash --assert 781
jaba balances store.json account ar --assert 241
jaba balances store.json account goods --assert 50
jaba balances store.json account equity --assert 1000
jaba balances store.json account re --assert 80

jaba balances store.json list

jaba balances store.json list --skip-zero --json > end_balances.json
