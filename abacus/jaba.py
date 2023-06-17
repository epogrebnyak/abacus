"""
*jaba* is a double entry accounting manager.

Commands: 
  jaba chart - define a chart of accounts
  jaba store - post entries and close accounting period
  jaba names - hold longer names to accounts
  jaba report - produce trail balance and financial reports
  jaba balances - show account balances

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
  jaba chart <chart_file> list [--validate [--quiet]] [--json]
  jaba chart <chart_file> create <store_file> [--start-file <start_balances_file>]
  jaba store <store_file> init <chart_file> [<start_balances_file>]
  jaba store <store_file> post <dr_account> <cr_account> <amount> [--adjust] [--post-close]
  jaba store <store_file> post --dr <dr_account> --cr <cr_account> --amount <amount> [--adjust] [--post-close]
  jaba store <store_file> close
  jaba store <store_file> list (--start | --business | --adjust | --close | --post-close | --all) [--json]
  jaba store <store_file> show <account_name> [--balance] [--net] [--json]
  jaba store <store_file> assert <account_name> <amount> [--net]
  jaba names <name_file> touch
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list [--json]
  jaba report <store_file> (-i | --income-statement) [--names <name_file>] [--rich] [--json]
  jaba report <store_file> (-b | --balance-sheet) [--names <name_file>] [--rich] [--json]
  jaba report <store_file> (-t | --trial-balance) [(--credit | --debit) [--sum]] [--json]
  jaba balances <store_file> show [--end] [--json]
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


def main():
    arguments = docopt(__doc__, version="0.4.3")
    if arguments["--args"]:
        print(arguments)
    if arguments["chart"]:
        path = Path(arguments["<chart_file>"])
        if arguments["unlink"]:
            if path.exists():
                path.unlink()
            sys.exit(0)
        if arguments["touch"]:
            if path.exists():
                sys.exit(f"Cannot create {path}, file already exists.")
            chart = Chart.empty()
            chart.save(path)
            pprint(chart.dict())
        try:
            chart = Chart.load(path)
        except FileNotFoundError:
            sys.exit(f"File not found: {path}")
        if arguments["list"]:
            pprint(chart.dict())
        if arguments["set"]:
            account_names = arguments["<account_names>"]
            if arguments["--re"] or arguments["--retained-earnings"]:
                chart.retained_earnings_account = arguments["<account_name>"]
                pprint(chart.retained_earnings_account)
            if arguments["--capital"]:
                chart.equity = account_names  # rename 'equity' to "capital"
                pprint(chart.equity)
            for flag in ["--assets", "--income", "--expenses", "--liabilities"]:
                if arguments[flag]:
                    attr = flag[2:]
                    setattr(chart, attr, account_names)
                    pprint(getattr(chart, attr))
            chart.save(path)
        if arguments["offset"]:
            key, names = (
                arguments["<account_name>"],
                arguments["<contra_account_names>"],
            )
            chart.contra_accounts[key] = names
            pprint(chart.contra_accounts)
            chart.save(path)
        if arguments["validate"]:
            try:
                chart.strong_validate()
            except AbacusError as e:
                sys.exit(repr(e))
        if arguments["create"]:
            chart = Chart.load(path)
            if arguments["--using"]:  # FIXME: does not work due to JSON issues
                starting_balances = read_json(arguments["<start_balances_file>"])
                book = chart.book(starting_balances)
            else:
                book = chart.book()
            book.save(arguments["<store_file>"])
            pprint(book.dict())
    elif arguments["names"]:
        pass
    elif arguments["store"]:
        path = arguments["<store_file>"]
        book = Book.load(path)
        if arguments["post"]:
            book.post(
                dr=arguments["<dr_account>"],
                cr=arguments["<cr_account>"],
                amount=arguments["<amount>"],
            )
            book.save(path)
        if arguments["close"]:
            book.close()
            book.save(path)
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
            pprint(show)
    elif arguments["report"]:
        path = arguments["<store_file>"]
        book = Book.load(path)
        if arguments["-i"] or arguments["--income-statement"]:
            pprint(book.income_statement().__dict__)
        if arguments["-b"] or arguments["--balance-sheet"]:
            pprint(book.balance_sheet().__dict__)
        if arguments["-t"] or arguments["--trial-balance"]:
            if arguments["--all"]:
                pprint(book.balances().data)
            else:
                pprint(book.nonzero_balances().data)
        if arguments["-a"] or arguments["--account"]:
            account_name = arguments["<account_name>"]
            actual = book.balances().data[account_name]
            if arguments["--assert"]:
                amount = Amount(arguments["<amount>"])
                if actual != amount:
                    raise AbacusError([account_name, actual, amount])
            pprint(actual)
    elif arguments["names"]:
        raise NotImplementedError  # yet


if __name__ == "__main__":
    main()
