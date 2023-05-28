#!/usr/bin/bash
python -m venv .env-cli
source .env-cli/bin/activate
pip install git+https://github.com/epogrebnyak/abacus.git
abacus show-config-file-options 
abacus chart -a cash,goods,ppe -e cogs,sga,rent,interest -c eq -r re -l dividend_due,loan -i sales -n sales discounts,cashback net_sales -n eq treasury_stock free_float -n ppe depreciation net_ppe > chart.json
abacus post --dr cash --cr eq --amount 1500
abacus post --dr goods --cr cash --amount 900
abacus post --dr cash --cr sales --amount 680
abacus post --dr cogs --cr goods --amount 500
abacus post --dr discounts --cr cash --amount 15
abacus post --dr cashback --cr cash --amount 15
abacus close --all
abacus report --income-statement --console
abacus report --balance-sheet --json
deactivate



