"""Abacus.

Usage:
  cli.py create chart [--output=<filename>]
  cli.py create balances --chart=<filename1> [--output=<filename2>]
  cli.py create store --chart=<filename1> [--start-balances=<filename2>] [--output=<filename3>]
  cli.py config (set | remove) --chart=<filename>
  cli.py config (set | remove) --store=<filename>
  cli.py add account <name> (--asset | --expense | --capital | --liability | --income) [--title=<title>] --chart=<filename>
  cli.py add accounts <names> (--asset | --expense | --capital | --liability | --income) --chart=<filename>
  cli.py set retained-earnings-account <name> [--title=<title>] --chart=<filename>
  cli.py set income-summary-account <name> [--title=<title>] --chart=<filename>
  cli.py add contra-account <name> --account=<name> --resulting-name=<resulting_name> [--resulting-title=<resulting_title>] --chart=<filename>
  cli.py add contra-accounts <names> --account=<name> --resulting-name=<resulting_name> --chart=<filename>
  cli.py verify chart --chart=<filename>
  cli.py verify store --store=<filename>
  cli.py add entry <dr_account> <cr_account> <amount> [--title=<title>] --store=<filename> [--adjustment | --post-close]
  cli.py add entry --dr=<dr_account> --cr=<cr_account> --amount=<amount> [--date=<date>] [--title=<title>] --store=<filename> [--adjustment | --post-close]
  cli.py mark --business-end --store=<filename>
  cli.py tb [--credit | --debit] [--sum] --store=<filename>
  cli.py net --all --store=<filename>
  cli.py net contra-accounts (--asset | --expense | --capital | --liability | --income | --permanent | --temporary | --all) --store=<filename>
  cli.py close (--all | --income | --expense | --isa) --store=<filename>
  cli.py report --income-balance --store=<filename> [--console]
  cli.py report --balance-sheet --store=<filename> [--console]
  cli.py show chart --store=<filename> [--console]
  cli.py show entries --store=<filename> [--console]
  cli.py show ledger --store=<filename> [--console]
  cli.py show balances --store=<filename> [--console]
  cli.py freeze --store=<filename1> [--output=<filename2>]
  cli.py save --store=<filename1> --to-excel=<filename2> [--overwrite]
  cli.py load --store=<filename1> --from-excel=<filename2> [--overwrite]
  cli.py (-h | --help)
  cli.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
#  naval_fate.py ship <name> move <x> <y> [--speed=<kn>]
#  naval_fate.py ship shoot <x> <y>
#  naval_fate.py mine (set|remove) <x> <y> [--moored | --drifting]

from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__, version="Naval Fate 2.0")
    print(arguments)
