poetry run python api.py chart erase --force
poetry run python api.py chart init
poetry run python api.py chart add --asset cash
poetry run python api.py chart add --asset ar
poetry run python api.py chart add --asset goods 
poetry run python api.py chart add --asset ppe --title "Property, plant, equipment" --code 10
poetry run python api.py chart add --capital equity
poetry run python api.py chart add --income sales
poetry run python api.py chart add --expense cogs
poetry run python api.py chart add --expense sga
poetry run python api.py chart set --retained-earnings "प्रतिधारित कमाई"
poetry run python api.py chart set --retained-earnings re
poetry run python api.py chart add --liability dividend_due
poetry run python api.py chart offset sales voids refunds
poetry run python api.py chart offset ppe depreciation
poetry run python api.py chart alias --operation invoice --debit ar --credit sales
poetry run python api.py chart alias --operation cost --debit cogs --credit goods
poetry run python api.py chart name ar "Accounts receivable"
poetry run python api.py chart name goods "Goods for resale"
poetry run python api.py chart name cogs "Cost of goods sold"
poetry run python api.py chart name sga "Selling, general, and adm. expenses"
poetry run python api.py chart show --json
poetry run python api.py chart show
