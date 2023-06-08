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
jaba store store.json close
jaba store store.json list
