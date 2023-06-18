"""
*jaba* is a double entry accounting manager.

Commands: 
  jaba chart    Define a chart of accounts.
  jaba ledger   Post entries and close accounting period.
  jaba names    Use longer account names.
  jaba report   Produce financial reports.
  jaba balances Show account balances.

Usage:
  jaba chart <chart_file> unlink
  jaba chart <chart_file> touch
  jaba chart <chart_file> set --assets <account_names>... [--quiet]
  jaba chart <chart_file> set --expenses <account_names>... [--quiet]
  jaba chart <chart_file> set --capital <account_names>... [--quiet]
  jaba chart <chart_file> set [--re | --retained-earnings] <account_name> [--quiet]
  jaba chart <chart_file> set --liabilities <account_names>... [--quiet]
  jaba chart <chart_file> set --income <account_names>... [--quiet]
  jaba chart <chart_file> offset <account_name> <contra_account_names>... [--quiet]
  jaba chart <chart_file> list [--validate] [--quiet] 
  jaba chart <chart_file> list [--validate] --json 
  jaba ledger <ledger_file> init <chart_file> [<starting_balances_file>] [--quiet]
  jaba ledger <ledger_file> post <dr_account> <cr_account> <amount> [--adjust] [--post-close] [--quiet]
  jaba ledger <ledger_file> post --dr <dr_account> --cr <cr_account> --amount <amount> [--adjust] [--post-close] [--quiet]
  jaba ledger <ledger_file> close [--quiet]
  jaba ledger <ledger_file> list [--start | --business | --adjust | --close | --post-close | --all] [--json]
  jaba balances <ledger_file> account <account_name> [--assert <amount>] [--net] [--json]
  jaba balances <ledger_file> trial [(--credit | --debit) [--sum]] [--json]
  jaba balances <ledger_file> list [--skip-zero] [--json]
  jaba names <name_file> touch
  jaba names <name_file> set <account_name> <title>
  jaba names <name_file> list [--json]
  jaba report <ledger_file> (-i | --income-statement) [--names <name_file>] [--rich] [--json]
  jaba report <ledger_file> (-b | --balance-sheet) [--names <name_file>] [--rich] [--json]
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

from abacus import AbacusError, Amount, Book, Chart, PlainTextViewer


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def echo(s):
    print(s, end=" ")


def print_added(account_names, where):
    print(f"Added {', '.join([f'<{a}>' for a in account_names])} to {where} accounts.")


def comma(xs):
    return ", ".join(xs)


def contra_phrase(key, names):
    return " ".join([key, "is offset by", comma(names)])


def print_chart(chart):
    re = chart.retained_earnings_account
    print("  Assets:     ", comma(chart.assets))
    print("  Capital:    ", comma(chart.equity + [re] if re else []))
    print("  Liabilities:", comma(chart.liabilities))
    print("  Income:     ", comma(chart.income))
    print("  Expenses:   ", comma(chart.expenses))
    if chart.contra_accounts:
        print("  Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("   ", contra_phrase(key, names))
    print("  Retained earnings account:", re)
    print("  Income summary account:   ", chart.income_summary_account)


def main():
    arguments = docopt(__doc__, version="0.4.3")
    if arguments["--args"]:
        pprint(arguments)
    if arguments["chart"]:
        path = Path(arguments["<chart_file>"])
        if arguments["unlink"]:
            echo("abacus chart:")
            if path.exists():
                path.unlink()
                print(f"Deleted {path}.")
                sys.exit(0)
            else:
                print("Cannot delete {path}, file does not exist.")
                sys.exit(1)
        if arguments["touch"]:
            echo("abacus chart:")
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
            chart = Chart.load(path)
            if arguments["--validate"]:
                try:
                    chart.strong_validate()
                    if not arguments["--json"]:
                        print("abacus chart: Accounts validated.")
                except AbacusError as e:
                    sys.exit(repr(e))
            if arguments["--json"]:
                print(json.dumps(chart.dict()))
            else:
                print("abacus chart: Listing accounts...")
                print_chart(chart)
        if arguments["set"]:
            echo("abacus chart:")
            account_names = arguments["<account_names>"]
            if arguments["--re"] or arguments["--retained-earnings"]:
                chart.retained_earnings_account = arguments["<account_name>"]
                print(
                    f"<{chart.retained_earnings_account}> was set as retained earnings account."
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
            print("abacus chart:", contra_phrase(key, names))
    elif arguments["names"]:
        pass
    elif arguments["ledger"]:
        if arguments["init"]:
            chart = Chart.load(arguments["<chart_file>"])
            start_file = arguments["<starting_balances_file>"]
            # FIXME: does not work due to JSON issues
            if start_file:
                starting_balances = read_json(start_file)
                book = chart.book(starting_balances)
            else:
                book = chart.book()
            book.save(arguments["<ledger_file>"])
            print("abacus ledger: Initialized data ledger (ledger).")
            sys.exit(0)
        path = arguments["<ledger_file>"]
        book = Book.load(path)
        if arguments["post"]:
            dr = arguments["<dr_account>"]
            cr = arguments["<cr_account>"]
            amount = arguments["<amount>"]
            book.post(dr, cr, amount)
            book.save(path)
            print(
                f"abacus ledger: Debited <{dr}> and credited <{cr}> with amount of {amount}."
            )
        if arguments["close"]:
            book.close()
            book.save(path)
            print("abacus ledger: Added closing entries to ledger.")
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
        path = arguments["<ledger_file>"]
        book = Book.load(path)
        if arguments["-i"] or arguments["--income-statement"]:
            from abacus.book import ledger_for_income_statement
            pprint(ledger_for_income_statement(book).balances().data)
            if arguments["--json"]:
                pprint(book.income_statement().__dict__)
            else:
                print("abacus report: Income statement")
                print(PlainTextViewer(rename_dict={}).show(book.income_statement()))
        if arguments["-b"] or arguments["--balance-sheet"]:
            if arguments["--json"]:
                pprint(book.balance_sheet().__dict__)
            else:
                print("abacus report: Balance sheet")
                print(PlainTextViewer(rename_dict={}).show(book.balance_sheet()))
    elif arguments["balances"]:
        path = arguments["<ledger_file>"]
        book = Book.load(path)
        account_name = arguments["<account_name>"]
        if arguments["account"] and arguments["--assert"]:
                actual = book.balances().data[account_name]
                amount = Amount(arguments["<amount>"])
                if actual != amount:
                    sys.exit(
                        f"abacus assert (failed): Account <{account_name}> expected {amount}, got {actual}"
                    )
                echo("abacus assert (passed):")
                print(account_info(account_name, amount))
        if arguments["account"] and not arguments["--assert"]:   
            amount = book.balances().data[account_name]
            if arguments["--json"]:
                print(json.dumps({account_name: amount}))
            else:
                echo("abacus balances:")
                print(account_info(account_name, amount))
        elif arguments["list"]:
            path = arguments["<ledger_file>"]
            book = Book.load(path)
            if not arguments["--json"]:
                    print("abacus balances: list account balances")
            if arguments["--skip-zero"]:
                print(json.dumps(book.nonzero_balances().data))
            else:
                print(json.dumps(book.balances().data))
            if arguments["trial"]:
                raise NotImplementedError  # yet
    elif arguments["names"]:
        raise NotImplementedError  # yet


def account_info(account_name, amount):
    return f"Account <{account_name}> balance is {amount}."


if __name__ == "__main__":
    main()
