# TODO:aff more codes from https://www.audit-it.ru/plan_schetov/
poetry run python api.py chart erase --force
poetry run python api.py chart init
poetry run python api.py chart add --asset cash --code 50
poetry run python api.py chart add --asset ar --title "Accounts receivable" --code "620"
poetry run python api.py chart add --asset goods --title "Goods for resale"
poetry run python api.py chart add --asset ppe
poetry run python api.py chart set ppe --title "Property, plant, equipment" 
poetry run python api.py chart set ppe --code 01
poetry run python api.py chart add --capital equity
poetry run python api.py chart add --income sales
poetry run python api.py chart add --expense cogs
poetry run python api.py chart add --expense sga --title "Selling, general, and adm. expenses"
poetry run python api.py chart set --retained-earnings "प्रतिधारित कमाई"
poetry run python api.py chart set --retained-earnings re
poetry run python api.py chart add --liability dividend_due
poetry run python api.py chart add --liability ap --title "Accounts payable" --code "621"
poetry run python api.py chart offset sales voids refunds
poetry run python api.py chart offset ppe depreciation
poetry run python api.py chart set depreciation --code 02
poetry run python api.py chart alias --operation invoice --debit ar --credit sales --requires cost
poetry run python api.py chart alias --operation cost --debit cogs --credit goods --requires invoice
poetry run python api.py chart show --json
poetry run python api.py chart show
