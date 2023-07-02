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
  bx chart name <account_name> --title <title>
  bx chart list [--json]
  bx ledger start [--file <balances_file>] [--dry-run]
  bx ledger post --debit <dr> --credit <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post <dr> <cr> <amount> [--adjust] [--post-close]
  bx ledger close
  bx ledger list [--start | --business | --adjust | --close | --post-close] [--json]
  bx show report --income-statement [--json] 
  bx show report --balance-sheet [--json] 
  bx show balances [--all] [--trial] [--json]
  bx show account <account_name>
  bx assert <account_name> <amount>
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

from docopt import docopt

from abacus import Amount, Book, PlainTextViewer
from abacus.chart import QualifiedChart


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


def init(force: bool = False, directory=cwd()):
    # FIXME: change this command to creating abacus.toml
    loc = Location(directory)
    create_object(loc.chart, force, QualifiedChart.empty())


def create_object(path: Path, force: bool, default_object: QualifiedChart):
    if path.exists() and not force:
        sys.exit(f"Cannot create {path}, file already exists.")
    default_object.save(path)
    name = (
        "chart"
        if isinstance(default_object, QualifiedChart)
        else default_object.__class__.__name__.lower()
    )
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
    print("  Assets:     ", comma(chart.base.assets))
    print("  Capital:    ", comma(chart.base.equity))
    print("  Liabilities:", comma(chart.base.liabilities))
    print("  Income:     ", comma(chart.base.income))
    print("  Expenses:   ", comma(chart.base.expenses))
    if chart.contra_accounts:
        print("  Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("    -", contra_phrase(key, names))
    print("  Retained earnings account:", re or "not specified")
    print("  Income summary account:   ", chart.income_summary_account)


def chart_show(chart: QualifiedChart, json_flag: bool):
    if json_flag:
        print(json.dumps(chart.dict()))
    else:
        print_chart(chart)


def name_command(account_name, title):
    chart, path = load_chart(directory=cwd())
    chart.set_name(account_name, title)
    print("Long name for", account_name, "is", title + ".")
    chart.save(path)


def end():
    # Implementation for "bx end"
    print("This is an alias.")


def debug(arguments):
    print(arguments)


def load_chart(directory):
    path = Location(directory).chart
    if path.exists():
        chart = safe_load(QualifiedChart, path)
    else:
        chart = QualifiedChart.empty()
    return chart, path


def chart_command(arguments, directory=cwd()):
    chart, path = load_chart(directory)
    if arguments["set"]:
        if arguments["--retained-earnings"]:
            re = arguments["<re_account_name>"]
            chart.set_retained_earnings(account_name=re)
            chart.save(path)
            print("Set", re, "as retained earnings account.")
            sys.exit(0)
        account_names = arguments["<account_names>"]
        for attribute in ["assets", "equity", "liabilities", "income", "expenses"]:
            if arguments["--" + attribute]:
                setattr(chart.base, attribute, account_names)
                break
        chart.save(path)
        print(
            "Set",
            comma(account_names),
            "as",
            attribute,
            "accounts." if len(account_names) > 1 else "account.",
        )
    elif arguments["offset"]:
        key = arguments["<account_name>"]
        names = arguments["<contra_account_names>"]
        chart.offset(key, names)
        chart.save(path)
        print("Modified chart,", contra_phrase(key, names) + ".")
    elif arguments["name"]:
        account_name, title = arguments["<account_name>"], arguments["<title>"]
        chart.set_name(account_name, title)
        chart.save(path)
        print("Long name for", account_name, "is", title + ".")
    elif arguments["list"]:
        chart_show(chart, arguments["--json"])


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ledger_command(arguments, directory=cwd()):
    ledger_path = Location(directory).entries
    if arguments["start"]:
        chart, _ = load_chart(directory)
        chart.qualify()
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
    if arguments["list"]:
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
    rename_dict = book.chart.names
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


def balances_command(arguments):
    # bx balances [--all]
    path = Location(directory=cwd()).entries
    book = safe_load(Book, path)
    if arguments["--all"]:
        data = book.balances()
    else:
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
        # FIXME
        print(show)
    else:
        # FIXME
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
    elif arguments["report"] and arguments["show"]:
        # bx show report
        report_command(arguments)
    elif arguments["balances"] and arguments["show"]:
        # bx show balances
        balances_command(arguments)
    elif arguments["account"] and arguments["show"]:
        # bx show account <account_name>
        print_account_balance(account_name=arguments["<account_name>"])
    elif arguments["assert"]:
        account_name, amount = arguments["<account_name>"], arguments["<amount>"]
        assert_account_balance(account_name, amount)
    else:
        sys.exit("Command not recognized. Use bx --help for reference.")     


if __name__ == "__main__":
    main()
