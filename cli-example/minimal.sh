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

jaba store store.json init chart.json
jaba store store.json post --dr cash --cr equity --amount 1000
jaba store store.json post goods cash 300
jaba store store.json post cogs goods 250
jaba store store.json post ar sales 440
jaba store store.json post discounts ar 41
jaba store store.json post cash ar 150
jaba store store.json post sga cash 69
jaba store store.json close
jaba store store.json list --quiet

jaba report store.json --balance-sheet
jaba report store.json --income-statement

jaba balances store.json list --skip-zero --json

jaba balances store.json list goods --json
jaba balances store.json list goods

jaba balances store.json assert cash 781
jaba balances store.json assert ar 241
jaba balances store.json assert goods 50
jaba balances store.json assert equity 1000
jaba balances store.json assert re 80

jaba balances store.json end > end_balances.json
