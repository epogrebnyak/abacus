"""Abacus.

Usage:
  cli.py init chart
  cli.py config (set | remove) --chart=<filename>
  cli.py config (set | remove) --store=<filename>
  cli.py add account <name> (--asset | --expense | --capital | --retained-earnings | --liability | --income) [--title=<title>] --chart=<filename>
  cli.py add account <name> --isa [--title=<title>] --chart=<filename>
  cli.py add accounts <names> (--asset | --expense | --capital | --liability | --income) --chart=<filename>
  cli.py add contra-account <name> --account=<name> --resulting-name=<resulting_name> [--resulting-title=<resulting_title>] --chart=<filename>
  cli.py add contra-accounts <names> --account=<name> --resulting-name=<resulting_name> --chart=<filename>
  cli.py init balances --chart=<filename>
  cli.py init store --chart=<filename1> [--balances=<filename2>]
  cli.py verify chart --chart=<filename>
  cli.py verify store --store=<filename>
  cli.py add entry <dr_account> <cr_account> <amount> [--title=<title>] --store=<filename> [--adjustment | --post-close]
  cli.py add entry --dr=<dr_account> --cr=<cr_account> --amount=<amount> [--title=<title>] --store=<filename> [--adjustment | --post-close]
  cli.py mark --business-end --store=<filename>
  cli.py tb [--credit | --debit] [--sum] --store=<filename>
  cli.py net contra-accounts (--asset | --expense | --capital | --liability | --income | --permanent | --temporary | --all) --store=<filename>
  cli.py close (--all | --income | --expense | --isa) --store=<filename>
  cli.py report --income-balance --store=<filename> [--console]
  cli.py report --balance-sheet --store=<filename> [--console]
  cli.py show chart --store=<filename>
  cli.py show entries --store=<filename>
  cli.py show ledger --store=<filename>
  cli.py show balances --store=<filename>
  cli.py freeze --store=<filename>
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


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    print(arguments)