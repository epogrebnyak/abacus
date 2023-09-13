poetry run python api.py account cash
poetry run python api.py account cash --assert 550
poetry run python api.py account cash --assert 551 || echo "Captured failure."
poetry run python api.py balances 
poetry run python api.py balances --nonzero
poetry run python api.py balances --nonzero > balances.json
