python abacus.py touch chart --output=chart.json
python abacus.py config --chart=chart.json
python abacus.py set accounts --assets cash prepaid_rent --capital equity --retained-earnings retained_earnings --liabilities loan --expenses rent salaries interest
python abacus.py set account --income sales --contra-accounts discounts cashback --resulting-account net_sales
python abacus.py validate chart
python abacus.py touch balances --chart chart.json --output start_balances.json
python abacus.py config --start-balances start_balances.json
python abacus.py touch postings --output postings.json
python abacus.py config --postings postings.json
python abacus.py entry --dr cash --cr equity --amount 1500
python abacus.py mark --business-period-end
python abacus.py entry --dr rent --cr prepaid_rent --amount 30 --adjust 
python abacus.py close --all
python abacus.py entry --dr retained_earning --cr dividend_due --amount 10 --post-close 
python abacus.py report --income-statement --console
python abacus.py report --balance-sheet --console
python abacus.py balances --output end_balances.json