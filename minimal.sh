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
jaba store store.json post cash equity 1500 
jaba store store.json post inventory cash 300 
jaba store store.json post cogs inventory 250 
jaba store store.json post ar sales 440
jaba store store.json post discounts ar 41
jaba store store.json post cash ar 250
jaba store store.json post sga cash 59
jaba store store.json close
jaba store store.json list

jaba store store.json report -b
jaba store store.json report -i
jaba store store.json balances
