jaba chart chart.json create
jaba chart chart.json set --assets cash ar inventory
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba chart chart.json set --liabilities ap dividend_due
jaba chart chart.json set --income sales
jaba chart chart.json set --expenses cogs sga
jaba chart chart.json offset discounts cashback --contra sales
jaba chart chart.json validate
jaba chart chart.json list
