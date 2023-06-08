call jaba chart chart.json touch
call jaba chart chart.json set --assets cash ar inventory ppe
call jaba chart chart.json set --capital equity
call jaba chart chart.json set --retained-earnings re
call jaba chart chart.json set --liabilities ap dividend_due
call jaba chart chart.json set --income sales
call jaba chart chart.json set --expenses cogs sga 
call jaba chart chart.json offset ppe depreciation
call jaba chart chart.json offset sales discounts cashback
call jaba chart chart.json validate
call jaba chart chart.json list

call jaba chart chart.json create store.json 
call jaba store store.json post cash equity 1500 
call jaba store store.json close
call jaba store store.json list

