poetry run python api.py ledger erase --force
poetry run python api.py ledger open --start balances.json
poetry run python api.py ledger show
poetry run python api.py ledger erase --force
poetry run python api.py ledger open
poetry run python api.py ledger post cash equity 1000
poetry run python api.py ledger post goods cash 700
poetry run python api.py ledger post --operation invoice 850 cost 650
poetry run python api.py ledger post cash ar 400
poetry run python api.py ledger post sga cash 150
poetry run python api.py ledger close
poetry run python api.py ledger show
