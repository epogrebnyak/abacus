poetry run python cli.py --help
echo y | poetry run python cli.py extra unlink
poetry run python cli.py init
poetry run python cli.py add asset:cash asset:prepaid_services 
poetry run python cli.py add capital:equity liability:loan
poetry run python cli.py add income:services contra:services:cashback
poetry run python cli.py add expense:salaries,marketing,interest
poetry run python cli.py post --debit cash --credit equity --amount 1000
poetry run python cli.py post --debit cash --credit loan --amount 3000
poetry run python cli.py post --debit prepaid_services --credit cash --amount 1800
poetry run python cli.py post --debit salaries --credit cash --amount 2000
poetry run python cli.py post --debit cash --credit services --amount 3500
poetry run python cli.py post --debit cashback --credit cash --amount 200
poetry run python cli.py post --debit interest --credit cash --amount 225
poetry run python cli.py close
poetry run python cli.py post --debit marketing --credit prepaid_services --amount 1200
poetry run python cli.py report -tbi
poetry run python cli.py report -a
poetry run python cli.py report -a > balances.json


