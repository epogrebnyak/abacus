"""Double entry accounting manager.

Usage:
  bx init [--force]
  bx chart set --assets <account_names>...
  bx chart set (--capital | --equity) <account_names>...
  bx chart set --retained-earnings <account_name>
  bx chart set --liabilities <account_names>...
  bx chart set --income <account_names>...
  bx chart set --expenses <account_names>...
  bx chart offset <account_name> (--contra-accounts <contra_account_names>...)
  bx chart show [--json]
  bx ledger start [--file <balances_file>] [--dry-run]
  bx ledger post --debit <dr> --credit <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post --dr <dr> --cr <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post <dr> <cr> <amount> [--adjust] [--post-close]
  bx ledger close
  bx name <account_name> <title>
  bx name <account_name> ((-t | --title) <title>)
  bx report (-i | --income-statement) 
  bx report (-b | --balance-sheet) 
  bx report (-t | --trial-balance)
  bx balances (--nonzero | --all)
  bx balances <account_name> [--assert <amount>]
  bx end
  bx debug --args

Options:
  -h --help     Show this help message.
  --version     Show version.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from docopt import docopt

from abacus import Chart
from abacus.chart import Chart


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


import json


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


def ledger_start(file, dry_run):
    # Implementation for "bx ledger start"
    pass


def ledger_post(dr, cr, amount, adjust, post_close):
    # Implementation for "bx ledger post"
    pass


def ledger_close():
    # Implementation for "bx ledger close"
    pass


def name(account_name, title):
    # Implementation for "bx name"
    pass


def report_income_statement():
    """Implementation for 'bx report -i'"""
    print("i")


def report_balance_sheet():
    """Implementation for 'bx report -b'"""
    print("b")


def report_trial_balance():
    """Implementation for 'bx report -t'"""
    print("t")


def account_balance(account_name: str):
    print(account_name)


def assert_account_balance(account_name: str, assert_amount: str):
    print(account_name, assert_amount)


def balances(all_flag: bool, nonzero_flag: bool, json: bool = False):
    print(all_flag, nonzero_flag)


def end():
    # Implementation for "bx end"
    pass


def debug(arguments):
    print(arguments)


def get_chart():
    path = Location(directory=cwd()).chart
    return safe_load(Chart.parse_file, path)


def chart_command(arguments):
    path = Location(directory=cwd()).chart
    chart = safe_load(Chart.parse_file, path)
    if arguments["set"]:
        account_names = arguments["<account_names>"]
        field = ""
        if arguments["--assets"]:
            chart.assets = account_names
            field = "assets"
        elif arguments["--capital"] or arguments["--equity"]:
            chart.equity = account_names
            field = "equity (capital)"
        elif arguments["--liabilities"]:
            chart.liabilities = account_names
            field = "liabilities"
        elif arguments["--income"]:
            chart.income = account_names
            field = "income"
        elif arguments["--expenses"]:
            chart.expenses = account_names
            field = "expenses"
        if field:
            print(
                "Assigned",
                comma(account_names),
                "as",
                field,
                "accounts." if len(account_names) > 1 else "account.",
            )
        if arguments["--retained-earnings"]:
            account_name = arguments["<account_name>"]
            chart.retained_earnings_account = account_name
            print("Assigned", account_name, "as retained earnings account.")
        chart.save(path)
    elif arguments["offset"]:
        key = arguments["<account_name>"]
        names = arguments["<contra_account_names>"]
        chart.contra_accounts[key] = names
        chart.save(path)
        print("Modified chart,", contra_phrase(key, names) + ".")
    elif arguments["show"]:
        chart_show(chart, arguments["--json"])


def main():
    arguments = docopt(__doc__, version="0.4.13")

    if arguments["init"]:
        init(arguments["--force"])
    elif arguments["debug"]:
        debug(arguments)
    elif arguments["chart"]:
        chart_command(arguments)
    elif arguments["ledger"] and arguments["start"]:
        ledger_start(arguments["--file"], arguments["--dry-run"])
    elif arguments["ledger"] and arguments["post"]:
        ledger_post(
            arguments["<dr>"],
            arguments["<cr>"],
            arguments["<amount>"],
            arguments["--adjust"],
            arguments["--post-close"],
        )
    elif arguments["ledger"] and arguments["close"]:
        ledger_close()
    elif arguments["name"]:
        name(arguments["<account_name>"], arguments["<title>"])
    elif arguments["report"]:
        if arguments["-i"] or arguments["--income-statement"]:
            report_income_statement()
        elif arguments["-b"] or arguments["--balance-sheet"]:
            report_balance_sheet()
        elif arguments["-t"] or arguments["--trail-balance"]:
            report_trial_balance()
    elif arguments["balances"]:
        if (name := arguments["<account_name>"]) and not arguments["--assert"]:
            account_balance(name)
        if (name := arguments["bx ledger post <account_name>"]) and (
            amount := arguments["<amount>"]
        ):
            assert_account_balance(name, amount)
        if (is_all := arguments["--all"]) or (is_nonzero := arguments["--nonzero"]):
            balances(is_all, is_nonzero)
    elif arguments["end"]:
        end()


if __name__ == "__main__":
    main()
