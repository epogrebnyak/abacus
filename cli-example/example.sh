poetry run abacus chart -a cash,goods,ppe -e cogs,sga,rent,interest -c eq -r re -l dividend_due,loan -i sales -n sales discounts,cashback net_sales -n eq treasury_stock free_float -n ppe depreciation net_ppe > chart.json
poetry run abacus empty-store > entries.json
poetry run abacus post --dr cash --cr eq --amount 1500 --store entries.json
poetry run abacus post --dr goods --cr cash --amount 900 --store entries.json
poetry run abacus post --dr cash --cr sales --amount 680 --store entries.json
poetry run abacus post --dr cogs --cr goods --amount 500 --store entries.json
poetry run abacus post --dr discounts --cr cash --amount 15 --store entries.json
poetry run abacus post --dr cashback --cr cash --amount 15 --store entries.json
#poetry run abacus close --all
#poetry run abacus report --income-statement --console
#poetry run abacus report --balance-sheet --json
