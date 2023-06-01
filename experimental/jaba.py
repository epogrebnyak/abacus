"""
`jaba` is a minimal accounting manager.

Usage:
jaba create chart <file>
jaba chart <chart_file> add --assets <account_names>
jaba chart <chart_file> add --expenses <account_names>  
jaba chart <chart_file> add --capital <account_names>  
jaba chart <chart_file> add --liabilities <account_names>   
jaba chart <chart_file> add --income <account_names>   
jaba chart <chart_file> contains <account_names>
jaba chart <chart_file> list
jaba chart <file> offset --name <account_name> --resulting-name <new_account_name> --contra-accounts <account_names>   
jaba create names <name_file>
jaba names <name_file> add <var> <title> 
jaba names <name_file> list
jaba create store <store_file> [--start-balances start_balances.json] [--verify-with chart.json]
jaba store <store_file> add entry --dr dr_account --cr cr_account --amount amount
jaba store <store_file> add mark <event>
jaba store <store_file> add multiple --dr account,amount [--dr account,amount] --cr account,amount [--cr account,amount]
jaba store <store_file> list --all
jaba store <store_file> list [--start-balances] [--entry] [--rename-account] [--mark-event]
jaba store <store_file> <chart_file> report -t > trial_balance.json
jaba store <store_file> <chart_file> close --contra-income --contra-expenses
jaba store <store_file> <chart_file> close --income --expenses --isa 
jaba store <store_file> <chart_file> report -i > income_statement.json [--names <name_file>] 
jaba store <store_file> <chart_file> report -b > balance_sheet.json [--names <name_file>] 
jaba store <store_file> <chart_file> report -e > end_balances.json 

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__, version="pre_alpha")
    print(arguments)
