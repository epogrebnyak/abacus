poetry run python api.py accounts show cash
poetry run python api.py accounts show cash --assert 550
poetry run python api.py accounts show --balances
poetry run python api.py accounts show --balances --nonzero
poetry run python api.py accounts show --balances --nonzero > balances.json
