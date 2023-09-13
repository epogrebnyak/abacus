poetry run python api.py ledger erase --force
poetry run python api.py ledger init balances.json
poetry run python api.py ledger show
#poetry run python api.py accounts show null --assert-balance 0
poetry run python api.py ledger erase --force
poetry run python api.py ledger init
poetry run python api.py ledger post cash equity 1000
poetry run python api.py ledger post goods cash 700
poetry run python api.py ledger post --operation invoice 850 cost 650
poetry run python api.py ledger post cash ar 400
poetry run python api.py ledger post sga cash 150
poetry run python api.py ledger close
poetry run python api.py ledger show
