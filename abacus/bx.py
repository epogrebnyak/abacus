"""Double entry accounting manager.

Usage:
  bx init [--force]
  bx chart set --assets <account_names>...
  bx chart set --equity <account_names>...
  bx chart set --retained-earnings <re_account_name>
  bx chart set --liabilities <account_names>...
  bx chart set --income <account_names>...
  bx chart set --expenses <account_names>...
  bx chart offset <account_name> (--contra-accounts <contra_account_names>...)
  bx chart show [--json]
  bx ledger start [--file <balances_file> | --empty] [--dry-run]
  bx ledger post --debit <dr> --credit <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post <dr> <cr> <amount> [--adjust] [--post-close]
  bx ledger close
  bx ledger show (--start | --business | --adjust | --close | --post-close) [--json]
  bx name <account_name> --title <title>
  bx report --income-statement [--json] 
  bx report --balance-sheet [--json] 
  bx balances (--nonzero | --all) [--json]
  bx account <account_name> [--assert-balance <amount>]
  bx end
  bx debug

Options:
  -h --help     Show this help message.
  --version     Show version.
"""

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from docopt import docopt

from abacus import Amount, Book, Chart, Names, PlainTextViewer


def cwd() -> Path:
    return Path(os.getcwd())


@dataclass
class Location:
    directory: Path

    @property
    def chart(self, filename: str = "chart.json"):
        return self.directory / filename

    @property
    def entries(self, filename: str = "entries.json"):
        return self.directory / filename

    @property
    def names(self, filename: str = "names.json"):
        return self.directory / filename


def init(force: bool = False, directory=cwd()):
    loc = Location(directory)
    create_object(loc.chart, force, Chart.empty())
    create_object(loc.names, force, Names())


def create_object(path: Path, force: bool, default_object: Union[Chart, Names]):
    if path.exists() and not force:
        sys.exit(f"Cannot create {path}, file already exists.")
    default_object.save(path)
    name = default_object.__class__.__name__.lower()
    print(f"Created {name} at {path}.")


def safe_load(cls, path):
    try:
        return cls.parse_file(path)
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")


def comma(xs):
    if xs:
        return ", ".join(xs)
    else:
        return "not specified"


def contra_phrase(key, names):
    return " ".join([key, "account is offset by", comma(names)])


def print_chart(chart):
    re = chart.retained_earnings_account
    print("Chart of accounts")
    print("  Assets:     ", comma(chart.assets))
    print("  Capital:    ", comma(chart.equity + [re] if re else []))
    print("  Liabilities:", comma(chart.liabilities))
    print("  Income:     ", comma(chart.income))
    print("  Expenses:   ", comma(chart.expenses))
    if chart.contra_accounts:
        print("  Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("    -", contra_phrase(key, names))
    print("  Retained earnings account:", re or "not specified")
    print("  Income summary account:   ", chart.income_summary_account)


def chart_show(chart: Chart, json_flag: bool):
    if json_flag:
        print(json.dumps(chart.dict()))
    else:
        print_chart(chart)


def name_command(account_name, title):
    path = Location(directory=cwd()).names
    if path.exists():
        names = safe_load(Names, path)
    else:
        names = Names()
    names.names[account_name] = title
    print("Long name for", account_name, "is", title + ".")
    names.save(path)


def end():
    # Implementation for "bx end"
    print("This is an alias.")


def debug(arguments):
    print(arguments)


def load_chart(directory):
    path = Location(directory).chart
    if path.exists():
        chart = safe_load(Chart, path)
    else:
        chart = Chart.empty()
    return chart, path


def chart_command(arguments, directory=cwd()):
    chart, path = load_chart(directory)
    if arguments["set"]:
        if arguments["--retained-earnings"]:
            re_account_name = arguments["<re_account_name>"]
            chart.retained_earnings_account = re_account_name
            print("Set", re_account_name, "as retained earnings account.")
            chart.save(path)
            sys.exit(0)
        account_names = arguments["<account_names>"]
        for attribute in ["assets", "equity", "liabilities", "income", "expenses"]:
            if arguments["--" + attribute]:
                setattr(chart, attribute, account_names)
                break
        print(
            "Set",
            comma(account_names),
            "as",
            attribute,
            "accounts." if len(account_names) > 1 else "account.",
        )
        chart.save(path)
    elif arguments["offset"]:
        key = arguments["<account_name>"]
        names = arguments["<contra_account_names>"]
        chart.contra_accounts[key] = names
        chart.save(path)
        print("Modified chart,", contra_phrase(key, names) + ".")
    elif arguments["show"]:
        chart_show(chart, arguments["--json"])


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ledger_command(arguments, directory=cwd()):
    ledger_path = Location(directory).entries
    if arguments["start"]:
        chart, _ = load_chart(directory)
        chart.strong_validate()
        if arguments["--file"]:
            starting_balances = read_json(arguments["<balances_file>"])
        else:
            starting_balances = {}
        book = chart.book(starting_balances)
        if arguments["--dry-run"]:
            print("Created ledger in memory only, did not save (`--dry-run` mode).")
        else:
            book.save(ledger_path)
            print("Created ledger.")
        sys.exit(0)
    if arguments["show"]:
        show_command(arguments)
    book = safe_load(Book, ledger_path)
    if arguments["post"]:
        dr, cr, amount = arguments["<dr>"], arguments["<cr>"], arguments["<amount>"]
        if arguments["--adjust"]:
            raise NotImplementedError
        elif arguments["--post-close"]:
            raise NotImplementedError
        else:
            book.post(dr, cr, amount)
        print(f"Posted entry: debit {dr}, credit {cr}, amount {amount}.")
    if arguments["close"]:
        book.close()
        print("Added closing entries to ledger.")
    book.save(ledger_path)


def report_command(arguments, directory=cwd()):
    ledger_path = Location(directory).entries
    book = safe_load(Book, ledger_path)
    names_path = Location(directory).names
    rename_dict = safe_load(Names, names_path).names
    viewer = PlainTextViewer(rename_dict)
    if arguments["--income-statement"]:
        report = book.income_statement()
        if arguments["--json"]:
            print(json.dumps(report.__dict__))
        else:
            print("Income statement")
            print(viewer.show(report))
    if arguments["--balance-sheet"]:
        report = book.balance_sheet()
        if arguments["--json"]:
            print(json.dumps(report.__dict__))
        else:
            print("Balance sheet")
            print(viewer.show(report))


def account_info(account_name: str, amount: Amount):
    return f"account <{account_name}> balance is {amount}."

def human_name(account):
    return account.__class__.__name__
    # must return 'Сontra income' and 'Retained earnings' 

def print_account_balance(account_name: str, directory=cwd()):
    path = Location(directory).entries
    account = safe_load(Book, path).ledger()[account_name]
    print("Account", account_name)
    print("  Account type:", human_name(account))
    print("  Debits:", account.debits)
    print("  Credits:", account.credits)
    print("  Balance:", account.balance())


def assert_account_balance(account_name: str, assert_amount: str):
    path = Location(directory=cwd()).entries
    amount = safe_load(Book, path).balances()[account_name]
    expected_amount = Amount(assert_amount)
    if amount != expected_amount:
        sys.exit(
            f"Check (failed): expected {expected_amount}, got {amount}"
            f" for account {account_name}."
        )
    print("Check (passed):", account_info(account_name, amount))


def print_two_columns(data: dict):
    def maxlen(xs):
        return max(map(len, map(str, xs)))

    # n1 and n2 are column widths
    n1 = maxlen(data.keys())
    n2 = maxlen(data.values())
    for k, v in data.items():
        print(" ", k.ljust(n1, " "), str(v).rjust(n2, " "))


def account_command(arguments):
    # bx account <account_name> [--assert-balance <amount>]
    account_name = arguments["<account_name>"]
    if account_name:
        if arguments["--assert-balance"]:
            assert_account_balance(account_name, arguments["<amount>"])
        else:
            print_account_balance(account_name)


def balances_command(arguments):
    # bx balances (--nonzero | --all)
    path = Location(directory=cwd()).entries
    book = safe_load(Book, path)
    if arguments["--all"]:
        data = book.balances()
    elif arguments["--nonzero"]:
        data = book.nonzero_balances()
    if arguments["--json"]:
        print(json.dumps(data))
    else:
        print("Account balances")
        print_two_columns(data)


def show_command(arguments, directory=cwd()):
    path = Location(directory).entries
    book = safe_load(Book, path)
    if arguments["--start"]:
        show = book.starting_balances
    elif arguments["--business"]:
        show = book.entries.business
    elif arguments["--adjust"]:
        show = book.entries.adjustment
    elif arguments["--close"]:
        show = list(book.entries.closing.all())
    elif arguments["--post-close"]:
        show = book.entries.post_close
    if arguments["--json"]:
        print(show)
    else:
        print(show)


def main():
    arguments = docopt(__doc__, version="0.4.13")

    if arguments["init"]:
        init(arguments["--force"])
    elif arguments["debug"]:
        debug(arguments)
    elif arguments["chart"]:
        chart_command(arguments)
    elif arguments["ledger"]:
        ledger_command(arguments)
    elif arguments["name"]:
        name_command(arguments["<account_name>"], arguments["<title>"])
    elif arguments["report"]:
        report_command(arguments)
    elif arguments["balances"]:
        balances_command(arguments)
    elif arguments["account"]:
        account_command(arguments)
    elif arguments["end"]:
        end()


if __name__ == "__main__":
    main()
