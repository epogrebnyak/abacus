"""
`jaba` is a minimal accounting manager.

Usage:
  jaba chart <chart_file> touch
  jaba chart <chart_file> add assets <account_names>...
  jaba chart <chart_file> add expenses <account_names>...  
  jaba chart <chart_file> add capital <account_names>...
  jaba chart <chart_file> add retained-earnings <account_name>  
  jaba chart <chart_file> add liabilities <account_names>...   
  jaba chart <chart_file> add income <account_names>...   
  jaba chart <chart_file> offset <name> <new_name> <account_names>...  
  jaba chart <chart_file> list
  jaba names <name_file> touch
  jaba names <name_file> add <account_name> <title> 
  jaba names <name_file> list
  jaba store <store_file> create [--init start_balances.json [--use-chart chart.json]]
  jaba store <store_file> post <dr_account> <cr_account> <amount>
  jaba store <store_file> list [--head <n> | --tail <n> | --last ])
  jaba store <store_file> list [--from <event1>] [--to <event2>]
  jaba store <store_file> mark <event>
  jaba store <store_file> <chart_file> close (--contra-income --contra-expenses)
  jaba store <store_file> <chart_file> close (--income --expenses) 
  jaba store <store_file> <chart_file> close (--isa | --income-summary-account)
  jaba store <store_file> <chart_file> close --all
  jaba store <store_file> <chart_file> report (-i | --income-statement) [--names <name_file>] 
  jaba store <store_file> <chart_file> report (-b | --balance-sheet) [--names <name_file>] 
  jaba store <store_file> <chart_file> balances [--credit | --debit]
  jaba store <store_file> <chart_file> balance <account_name>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

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
