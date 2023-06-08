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

call jaba store store.json post --dr cash --cr equity --amount 1500
call jaba store store.json post inventory cash 300
call jaba store store.json post cogs inventory 250
call jaba store store.json post ar sales 440
call jaba store store.json post discounts ar 41
call jaba store store.json post cash ar 250
call jaba store store.json post sga cash 59
call jaba store store.json close
call jaba store store.json list

call jaba report store.json --balance-sheet
call jaba report store.json --income-statement
call jaba report store.json --trial-balance
call jaba report store.json --account re --assert 90

