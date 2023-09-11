poetry run python api.py account show cash
poetry run python api.py account show cash --assert 550
poetry run python api.py balances show 
poetry run python api.py balances show --nonzero
poetry run python api.py balances show --nonzero > balances.json
