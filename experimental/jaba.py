"""
`jaba` is a minimal accounting manager.

Usage:
  jaba chart <chart_file> create
  jaba chart <chart_file> add assets <account_names>...
  jaba chart <chart_file> add expenses <account_names>...  
  jaba chart <chart_file> add capital <account_names>...
  jaba chart <chart_file> add retained-earnings <account_name>  
  jaba chart <chart_file> add liabilities <account_names>...   
  jaba chart <chart_file> add income <account_names>...   
  jaba chart <chart_file> offset <name> <new_name> <account_names>...  
  jaba chart <chart_file> list
  jaba store <store_file> create --chart <chart_file> [--start start_balances.json]
  jaba store <store_file> post <dr_account> <cr_account> <amount>
  jaba store <store_file> close --all
  jaba store <store_file> list [--head <n> | --tail <n> | --last ]
  jaba store <store_file> list [--open | --usual | --adjust | --close | --post-close]
  jaba store <store_file> report (-i | --income-statement) [--names <name_file>] 
  jaba store <store_file> report (-b | --balance-sheet) [--names <name_file>] 
  jaba store <store_file> balances [--credit | --debit] [--sum]
  jaba store <store_file> balance <account_name>
  jaba names <name_file> create
  jaba names <name_file> add <account_name> <title> 
  jaba names <name_file> list

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

# jaba store <store_file> <chart_file> close (--contra-income --contra-expenses)
# jaba store <store_file> <chart_file> close (--income --expenses)
# jaba store <store_file> <chart_file> close (--isa | --income-summary-account)


from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__, version="pre_alpha")
    print(arguments)
    if arguments["chart"]:
        pass
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        pass
