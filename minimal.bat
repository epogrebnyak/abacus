call jaba chart chart.json create
call jaba chart chart.json set --assets cash ar inventory
call jaba chart chart.json set --capital equity
call jaba chart chart.json set --retained-earnings re
call jaba chart chart.json set --liabilities ap dividend_due
call jaba chart chart.json set --income sales
call jaba chart chart.json set --expenses cogs sga
call jaba chart chart.json offset discounts cashback --contra sales
call jaba chart chart.json validate
call jaba chart chart.json list
