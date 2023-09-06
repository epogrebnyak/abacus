poetry run python api.py chart erase --force
poetry run python api.py chart init
poetry run python api.py chart add --assets cash ar goods ppe
poetry run python api.py chart add --capital equity
poetry run python api.py chart add --income sales
poetry run python api.py chart add --expenses cogs sga
poetry run python api.py chart name ret "Retained earnings"
poetry run python api.py chart set --retained-earnings ret
poetry run python api.py chart offset sales voids refunds
poetry run python api.py chart offset ppe depreciation
poetry run python api.py chart name ar "Accounts receivable"
poetry run python api.py chart name goods "Goods for resale"
poetry run python api.py chart name cogs "Cost of goods sold"
poetry run python api.py chart name sga "Selling, general, and adm. expenses"
poetry run python api.py chart name ppe "Property, plant, equipment"
poetry run python api.py chart show --json
poetry run python api.py chart show



