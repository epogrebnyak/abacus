del chart.json
jaba chart chart.json touch
jaba chart chart.json set --assets cash ar inventory ppe
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba chart chart.json set --liabilities ap dividend_due
jaba chart chart.json set --income sales
jaba chart chart.json set --expenses cogs sga
jaba chart chart.json offset ppe depreciation
jaba chart chart.json offset sales discounts cashback
jaba chart chart.json validate
jaba chart chart.json list
jaba chart chart.json create store.json

jaba store store.json post --dr cash --cr equity --amount 1500
jaba store store.json post inventory cash 300
jaba store store.json post cogs inventory 250
jaba store store.json post ar sales 440
jaba store store.json post discounts ar 41
jaba store store.json post cash ar 250
jaba store store.json post sga cash 59
jaba store store.json close
jaba store store.json list

jaba report store.json --balance-sheet
jaba report store.json --income-statement
jaba report store.json --trial-balance
jaba report store.json --account re --assert 90
