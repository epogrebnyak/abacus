"""
jaba is a minimal accounting manager.

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
  jaba store <store_file> create --chart <chart_file> [--start <start_balances_file>]
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
from pathlib import Path
from pprint import pprint


def main():
    arguments = docopt(__doc__, version="0.4.3")
    print(arguments)
    if arguments["chart"]:
        path = Path(arguments["<chart_file>"])
        if arguments["create"]:
            from abacus.chart import empty_chart

            if not path.exists():
                path.write_text(empty_chart().json(indent=2), encoding="utf-8")
        elif arguments["add"]:
            pass
        elif arguments["list"]:
            from abacus.chart import Chart

            chart = Chart.parse_file(path)
            pprint(chart.dict())
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        pass


if __name__ == "__main__":
    main()
