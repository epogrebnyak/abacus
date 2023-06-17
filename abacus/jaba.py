"""
*jaba* is a double entry accounting manager.

Commands: 
  jaba chart    Define a chart of accounts.
  jaba store    Post entries and close accounting period.
  jaba names    Use longer account names.
  jaba report   Produce financial reports.
  jaba balances Show account balances.

Usage:
  jaba chart <chart_file> unlink
  jaba chart <chart_file> touch
  jaba chart <chart_file> set --assets <account_names>...
  jaba chart <chart_file> set --expenses <account_names>... 
  jaba chart <chart_file> set --capital <account_names>...
  jaba chart <chart_file> set [--re | --retained-earnings] <account_name>
  jaba chart <chart_file> set --liabilities <account_names>...
  jaba chart <chart_file> set --income <account_names>...
  jaba chart <chart_file> offset <account_name> <contra_account_names>...
  jaba chart <chart_file> list [--validate] [--quiet] [--json]
  jaba store <store_file> init <chart_file> [<starting_balances_file>]
  jaba store <store_file> post <dr_account> <cr_account> <amount> [--adjust] [--post-close]
  jaba store <store_file> post --dr <dr_account> --cr <cr_account> --amount <amount> [--adjust] [--post-close]
  jaba store <store_file> close
  jaba store <store_file> list [--start | --business | --adjust | --close | --post-close | --all] [--json] [--quiet]
  jaba names <name_file> touch
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list [--json]
  jaba report <store_file> (-i | --income-statement) [--names <name_file>] [--rich] [--json]
  jaba report <store_file> (-b | --balance-sheet) [--names <name_file>] [--rich] [--json]
  jaba balances <store_file> trial [(--credit | --debit) [--sum]] [--json]
  jaba balances <store_file> list [--skip-zero] [--json]
  jaba balances <store_file> list <account_name> [--net] [--json]
  jaba balances <store_file> assert <account_name> <amount> [--net]
  jaba balances <store_file> end
  jaba --args

Options:
  -h --help     Show this screen.
  --version     Show version.
  --args        Print arguments.
"""

import json
import sys
from pathlib import Path
from pprint import pprint

from docopt import docopt

from abacus import AbacusError, Amount, Book, Chart


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def echo(s):
    print(s, end=" ")


def print_added(account_names, where):
    print(f"Added {', '.join([f'<{a}>' for a in account_names])} to {where} accounts.")


def main():
    arguments = docopt(__doc__, version="0.4.3")
    if arguments["--args"]:
        pprint(arguments)
    if arguments["chart"]:
        echo("abacus chart:")
        path = Path(arguments["<chart_file>"])
        if arguments["unlink"]:
            if path.exists():
                path.unlink()
                print(f"Deleted {path}.")
                sys.exit(0)
            else:
                print("Cannot delete {path}, file does not exist.")
                sys.exit(1)
        if arguments["touch"]:
            if path.exists():
                sys.exit(f"Cannot create {path}, file already exists.")
            chart = Chart.empty()
            chart.save(path)
            print(f"Created {path}.")
        try:
            chart = Chart.load(path)
        except FileNotFoundError:
            sys.exit(f"File not found: {path}")
        if arguments["list"]:
            if not arguments["--json"]:
                echo("Listing accounts...")
            chart = Chart.load(path)
            if arguments["--validate"]:
                try:
                    chart.strong_validate()
                    if not arguments["--json"]:
                        print("accounts validated.")
                except AbacusError as e:
                    sys.exit(repr(e))
            print(json.dumps(chart.dict()))
        if arguments["set"]:
            account_names = arguments["<account_names>"]
            if arguments["--re"] or arguments["--retained-earnings"]:
                chart.retained_earnings_account = arguments["<account_name>"]
                print(
                    f"Set {chart.retained_earnings_account} as retained earnings account."
                )
            if arguments["--capital"]:
                chart.equity = account_names  # rename 'equity' to "capital"
                print_added(chart.equity, "equity")
            for flag in ["--assets", "--income", "--expenses", "--liabilities"]:
                if arguments[flag]:
                    attr = flag[2:]
                    setattr(chart, attr, account_names)
                    print_added(getattr(chart, attr), attr)
            chart.save(path)
        if arguments["offset"]:
            key, names = (
                arguments["<account_name>"],
                arguments["<contra_account_names>"],
            )
            chart.contra_accounts[key] = names
            chart.save(path)
            if len(names) > 1:
                print(
                    f"Contra accounts {', '.join([f'<{n}>' for n in names])} offset <{key}>."
                )

            else:
                print(f"Contra account <{names[0]}> offsets <{key}>.")
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        if arguments["init"]:
            chart = Chart.load(arguments["<chart_file>"])
            start_file = arguments["<starting_balances_file>"]
            # FIXME: does not work due to JSON issues
            if start_file:
                starting_balances = read_json(start_file)
                book = chart.book(starting_balances)
            else:
                book = chart.book()
            book.save(arguments["<store_file>"])
            print("abacus store: Initialized data store (ledger).")
            sys.exit(0)
        path = arguments["<store_file>"]
        book = Book.load(path)
        if arguments["post"]:
            dr = arguments["<dr_account>"]
            cr = arguments["<cr_account>"]
            amount = arguments["<amount>"]
            book.post(dr, cr, amount)
            book.save(path)
            print(
                f"abacus store: Debited <{dr}> and credited <{cr}> with amount of {amount}."
            )
        if arguments["close"]:
            book.close()
            book.save(path)
            print("abacus store: Added closing entries to ledger.")
        if arguments["list"]:
            show = book
            # [--start | --business | --adjust | --close | --post-close]
            if arguments["--start"]:
                show = book.starting_balance
            if arguments["--business"]:
                show = book.entries.business
            if arguments["--adjust"]:
                show = book.entries.adjust
            if arguments["--close"]:
                show = book.entries.closing
            if arguments["--post-close"]:
                show = book.entries.post_close
            if not arguments["--quiet"]:
                print(json.dumps(show))
    elif arguments["report"]:
        path = arguments["<store_file>"]
        book = Book.load(path)
        if arguments["-i"] or arguments["--income-statement"]:
            print("abacus report: Income statement")
            pprint(book.income_statement().__dict__)
        if arguments["-b"] or arguments["--balance-sheet"]:
            print("abacus report: Balance sheet")
            pprint(book.balance_sheet().__dict__)
    elif arguments["balances"]:
        path = arguments["<store_file>"]
        book = Book.load(path)
        account_name = arguments["<account_name>"]
        if arguments["list"] and not account_name:
            if not arguments["--json"]:
                print("abacus balances: list account balances")
            if arguments["--skip-zero"]:
                print(json.dumps(book.nonzero_balances().data))
            else:
                print(json.dumps(book.balances().data))
        if arguments["list"] and account_name:
            amount = book.balances().data[account_name]
            if arguments["--json"]:
                print(json.dumps({account_name: amount}))
            else:
                echo("abacus balances:")
                print(account_info(account_name, amount))
        if arguments["trial"]:
            raise NotImplementedError  # yet
        if arguments["end"]:
            # also check accounts were closed
            print(json.dumps(book.nonzero_balances().data))
        if arguments["assert"]:
            actual = book.balances().data[account_name]
            amount = Amount(arguments["<amount>"])
            if actual != amount:
                sys.exit(
                    f"abacus assert (failed): Account <{account_name}> expected {amount}, got {actual}"
                )
            echo("abacus assert (passed):")
            print(account_info(account_name, amount))
    elif arguments["names"]:
        raise NotImplementedError  # yet


def account_info(account_name, amount):
    return f"Account <{account_name}> balance is {amount}."


if __name__ == "__main__":
    main()
