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

from docopt import docopt

from abacus import Book, Chart, PlainTextViewer
from abacus.accounting_types import Amount


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
    # Implementation for "bx init"
    loc = Location(directory)
    create_chart(loc.chart, force)


def echo(s):
    print(s, end=" ")


def create_chart(path: Path, force: bool):
    if path.exists() and not force:
        sys.exit(f"Cannot create {path}, file already exists.")
    Chart.empty().save(path)
    print(f"Created chart of accounts at {path}.")


def safe_load(load_func, path):
    try:
        res = load_func(path)
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    return res


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


def name(account_name, title):
    # Implementation for "bx name"
    pass


def end():
    # Implementation for "bx end"
    print("This is an alias.")


def debug(arguments):
    print(arguments)


def load_chart(directory=cwd()):
    path = Location(directory).chart
    return safe_load(Chart.parse_file, path), path


def chart_command(arguments):
    chart, path = load_chart()
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


def ledger_command(arguments):
    path = Location(directory=cwd()).entries
    if arguments["start"]:
        chart, _ = load_chart()
        if arguments["--file"]:
            starting_balances = read_json(arguments["<balances_file>"])
        else:
            starting_balances = {}
        book = chart.book(starting_balances)
        if not arguments["--dry-run"]:
            book.save(path)
            print("Created ledger.")
        sys.exit(0)
    book = safe_load(Book.parse_file, path)
    if arguments["post"]:
        dr, cr, amount = arguments["<dr>"], arguments["<cr>"], arguments["<amount>"]
        if arguments["--adjust"]:
            raise NotImplementedError
        elif arguments["--post-close"]:
            raise NotImplementedError
        else:
            book.post(dr, cr, amount)
        book.save(path)
        print(f"Posted entry to ledger: debit {dr}, credit {cr}, amount {amount}).")
    if arguments["close"]:
        book.close()
        print("Added closing entries to ledger.")
    book.save(path)


def report_command(arguments):
    path = Location(directory=cwd()).entries
    book = Book.load(path)
    if arguments["--income-statement"]:
        if arguments["--json"]:
            print(json.dumps(book.income_statement().__dict__))
        else:
            print("Income statement")
            print(PlainTextViewer(rename_dict={}).show(book.income_statement()))
    if arguments["--balance-sheet"]:
        if arguments["--json"]:
            print(json.dumps(book.balance_sheet().__dict__))
        else:
            print("Balance sheet")
            print(PlainTextViewer(rename_dict={}).show(book.balance_sheet()))


def account_info(account_name: str, amount: Amount):
    return f"account <{account_name}> balance is {amount}."


def print_account_balance(account_name: str):
    path = Location(directory=cwd()).entries
    amount = Book.load(path).balances()[account_name]
    print(account_info(account_name, amount).capitalize())


def assert_account_balance(account_name: str, assert_amount: str):
    path = Location(directory=cwd()).entries
    amount = Book.load(path).balances()[account_name]
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
    book = Book.load(path)
    if arguments["--all"]:
        data = book.balances()
    elif arguments["--nonzero"]:
        data = book.nonzero_balances()
    print("Account balances")
    if arguments["--json"]:
        print(json.dumps(data))
    else:
        print_two_columns(data)


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
        name(arguments["<account_name>"], arguments["<title>"])
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
