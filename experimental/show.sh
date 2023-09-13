poetry run python api.py show account cash
poetry run python api.py show account cash --balance
poetry run python api.py show account cash --balance 550
poetry run python api.py show account cash --balance 551 || echo "Captured failure."
poetry run python api.py show balances 
poetry run python api.py show balances --nonzero
poetry run python api.py show balances --nonzero > balances.json
