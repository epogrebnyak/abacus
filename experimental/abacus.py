"""
Usage:
    abacus.py create chart --empty --output=chart.json
    abacus.py config --chart=chart.json
    abacus.py set accounts --assets cash prepaid_rent --capital equity --retained-earnings retained_earnings --liabilities loan --expenses rent salaries interest
    abacus.py set account --income sales --contra-accounts discounts cashback --resulting-account net_sales
    abacus.py validate chart
    abacus.py create balances --empty --chart chart.json --output start_balances.json
    abacus.py config --start-balances start_balances.json
    abacus.py config --entries entries.json
    abacus.py entry cash equity 1500
    abacus.py mark --business-period-end
    abacus.py entry rent prepaid_rent 30 --adjust 
    abacus.py close --all
    abacus.py entry retained_earning dividend_due 10 --post-close 
    abacus.py report --income-statement --console
    abacus.py report --balance-sheet --console
    abacus.py create balances --output end_balances.json
"""
