"""Double entry accounting manager.

Usage:
  bx chart start [-f | --force] [--chart-file <chart-file>]
  bx chart add  --asset <account_name> [--title <title>] [--code <code>] 
  bx chart add  --expense <account_name> [--title <title>] [--code <code>]
  bx chart add  --capital <account_name> [--title <title>] [--code <code>]
  bx chart add  --retained-earnings <account_name>
  bx chart add  --liability <account_name> [--title <title>] [--code <code>]
  bx chart add  --income <account_name> [--title <title>] [--code <code>]
  bx chart offset <account_name> <contra_account_names>...
  bx chart title <account_name> <title>
  bx chart code <account_name> <code>
  bx chart show [--json]
  bx operation set <name> --debit <dr_account> --credit <cr_account> [--describe <text>] [--requires <matched_name>]
  bx operation show [<name>]
  bx ledger start [--balances-file <balances_file>] [--dry-run]
  bx post operation (<operations> <amounts>)... 
  bx post operation (--title <title>) (<operations> <amounts>)... 
  bx post operation --title <title> --name <operation> --amount <amount> 
  bx post entry --debit <dr> --credit <cr> --amount <amount> [--adjust] [--after-close]
  bx post entry -t <title> --debit <dr> --credit <cr> --amount <amount> [--adjust] [--after-close]
  bx ledger close
  bx ledger list (--start | --business | --adjust | --close | --after-close | --all) [--json]
  bx report (-t | --trial-balance) [--json]
  bx report (-i | --income-statement) [--json] 
  bx report (-b | --balance-sheet) [--json] 
  bx accounts [--all] [--json]
  bx account <account_name>
  bx assert <account_name> <amount>
  bx erase (--chart | --ledger)

Options:
  -h --help     Show this help message.
  --version     Show version.
  --silent      Do not print to screen.
  -q --quiet    Same as --silent.
  -t --title    Entry or operation title.
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


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


@dataclass
class Location:
    directory: Path

    @property
    def chart(self, filename: str = "chart.json"):
        return self.directory / filename

    @property
    def entries(self, filename: str = "entries.json"):
        return self.directory / filename


def erase_chart(directory=cwd()):
    loc = Location(directory)
    loc.chart.unlink(missing_ok=True)


def erase_entries(directory=cwd()):
    loc = Location(directory)
    loc.entries.unlink(missing_ok=True)


def erase(arguments, directory=cwd()):
    if arguments["--chart"]:
        erase_chart(directory)
    if arguments["--ledger"]:
        erase_entries(directory)


def safe_load(cls, path):
    try:
        return cls.parse_file(path)
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")


def comma(chart, xs, fill=", "):
    if xs:
        return fill.join([chart.get_name(x) for x in xs])
    else:
        return "not specified"


def contra_phrase(chart, account_name, contra_account_names):
    return (
        chart.get_name(account_name)
        + " account is offset by "
        + comma(chart, contra_account_names)
    )


def ina(s):
    return f"<{s}>"


def step_print(chart, items):
    print(" ", comma(chart, items, "\n  "))


def step_print_factory(chart):
    def step_print(attribute):
        print(mapping()[attribute].capitalize())
        print(" ", comma(chart, getattr(chart.base, mapping()[attribute]), "\n  "))

    return step_print


def print_chart(chart):
    step_print = step_print_factory(chart)
    for key in mapping().keys():
        step_print(key)
    if chart.contra_accounts:
        print("Contra accounts")
        for key, names in chart.contra_accounts.items():
            print("  -", contra_phrase(chart, key, names) + ".")
    re = chart.retained_earnings_account
    print("Retained earnings account:", ina(re) or "not specified")
    print("Income summary account:", ina(chart.income_summary_account))


def chart_show(chart: QualifiedChart, json_flag: bool):
    if json_flag:
        print(json.dumps(chart.dict()))
    else:
        print_chart(chart)


def name_subcommand(chart, account_name, title):
    chart.set_name(account_name, title)
    print("Changed title for", ina(account_name), "account.")
    print("Account:", ina(account_name))
    print("  Title:", title)


def debug(arguments):
    print(arguments)


def load_chart(directory):
    path = Location(directory).chart
    if path.exists():
        chart = safe_load(QualifiedChart, path)
    else:
        chart = QualifiedChart.empty()
    return chart, path


def mapping():
    """This is a mapping from command line flags to Chart attributes.
    Using this mapping we will know that '--asset cash' will added to chart.assets."""
    return dict(
        [
            ("asset", "assets"),
            ("capital", "equity"),
            ("liability", "liabilities"),
            ("income", "income"),
            ("expense", "expenses"),
        ]
    )


def chart_command(arguments, directory=cwd()):
    chart, path = load_chart(directory)
    if arguments["add"] and arguments["--retained-earnings"]:
        re_account_name = arguments["<account_name>"]
        chart.set_retained_earnings(re_account_name)
        title = arguments["<title>"] or "Retained earnings"
        chart.set_name(re_account_name, title)
        chart.save(path)
        print("Retained earnings account:", chart.get_name(re_account_name))
        sys.exit(0)
    if arguments["add"]:
        account_name = arguments["<account_name>"]
        for flag in mapping().keys():
            if arguments["--" + flag]:
                attribute = mapping()[flag]
                account_names = getattr(chart.base, attribute)
                account_names.append(account_name)
                setattr(chart.base, attribute, account_names)
                break
        if arguments["--title"]:
            title = arguments["<title>"]
            name_subcommand(chart, account_name, title)
        if arguments["--code"]:
            raise NotImplementedError
        print("Added", ina(account_name), "account to chart.")
        step_print_factory(chart)(flag)
        chart.save(path)
    elif arguments["title"]:
        account_name = arguments["<account_name>"]
        title = arguments["<title>"]
        name_subcommand(chart, account_name, title)
        chart.save(path)
    elif arguments["offset"]:
        account_name = arguments["<account_name>"]
        contra_account_names = arguments["<contra_account_names>"]
        chart.offset(account_name, contra_account_names)
        print(
            "Modified chart,",
            contra_phrase(chart, account_name, contra_account_names) + ".",
        )
        chart.save(path)
    elif arguments["show"]:
        chart_show(chart, arguments["--json"])


def operations_command(arguments, directory=cwd()):
    chart, path = load_chart(directory)
    if arguments["set"]:
        name = arguments["<name>"]
        debit = arguments["<dr_account>"]
        credit = arguments["<cr_account>"]
        text = arguments["<text>"] or ""
        requires = arguments["<matched_name>"]
        print("  Operation:", name)
        print("Description:", text.capitalize())
        print("      Debit:", chart.get_name(debit))
        print("     Credit:", chart.get_name(credit))
        if requires:
            print("   Requires:", requires)
        chart.set_operation(name, debit, credit, text, requires)
        chart.save(path)
    elif arguments["show"]:
        print("Operations (put in table)")
        # FIXME: use table from table.py + add headers
        for name, op in chart.operations.items():
            print(
                name, op.debit, op.credit, op.description, op.requires or "", sep="\t| "
            )


def print_entry(chart, dr, cr, amount):
    print("Posted entry")
    print("   Debit:", chart.get_name(dr))
    print("  Credit:", chart.get_name(cr))
    print("  Amount:", amount)


def exit_requires(operation_name, requires):
    sys.exit(f"<{operation_name}> must be used with <{requires}> in one command call.")


def post_command2(arguments, directory=cwd()):
    ledger_path = Location(directory).entries
    book = safe_load(Book, ledger_path)
    if arguments["entry"]:
        dr = arguments["<dr>"]
        cr = arguments["<cr>"]
        amount = Amount(arguments["<amount>"])
        if arguments["--adjust"]:
            book.adjust(dr, cr, amount)
        elif arguments["--after-close"]:
            book.after_close(dr, cr, amount)
        else:
            book.post(dr, cr, amount)
        print_entry(book.chart, dr, cr, amount)
    if arguments["operation"]:
        operations = arguments["<operations>"]
        amounts = arguments["<amounts>"]
        for operation_name in operations:
            op = book.chart.get_operation(operation_name)
            if op.requires and op.requires not in operations:
                exit_requires(operation_name, op.requires)
        for operation_name, amount in zip(operations, amounts):
            book.post_operation(operation_name, amount)
            op = book.chart.get_operation(operation_name)
            print_entry(book.chart, op.debit, op.credit, amount)
    book.save(ledger_path)


def ledger_command(arguments, directory=cwd()):
    ledger_path = Location(directory).entries
    if arguments["start"]:
        chart, _ = load_chart(directory)
        chart.qualify()
        if arguments["--balances-file"]:
            starting_balances = read_json(arguments["<balances_file>"])
        else:
            starting_balances = {}
        book = chart.book(starting_balances)
        if arguments["--dry-run"]:
            print("Using --dry-run` mode: created ledger in memory only, did not save.")
        else:
            book.save(ledger_path)
            print(f"Saved ledger at {ledger_path}.")
        sys.exit(0)
    book = safe_load(Book, ledger_path)
    if arguments["list"]:
        show_command(arguments)
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
    # split on caps - must return 'Сontra income' and 'Retained earnings'


def print_account_balance(account_name: str, directory=cwd()):
    path = Location(directory).entries
    book = safe_load(Book, path)
    account = book.ledger()[account_name]
    print("   Account:", book.chart.get_long_name(account_name))
    print("Short name:", ina(account_name))
    print("      Type:", human_name(account))
    print("    Debits:", account.debits)
    print("   Credits:", account.credits)
    print("   Balance:", account.balance())


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
        print(k.ljust(n1, " "), str(v).rjust(n2, " "))


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
        print_two_columns({book.chart.get_name(k): v for k, v in data.items()})


def show_command(arguments, directory=cwd()):
    path = Location(directory).entries
    book = safe_load(Book, path)
    show = ""  # FIXME
    if arguments["--start"]:
        show = book.starting_balances
    elif arguments["--business"]:
        show = book.entries.business
    elif arguments["--adjust"]:
        show = book.entries.adjustment
    elif arguments["--close"]:
        show = list(book.entries.closing.all())
    elif arguments["--after-close"]:
        show = book.entries.after_close
    if arguments["--json"]:
        # FIXME
        print(show)
    else:
        # FIXME
        print(show)


def main():
    arguments = docopt(__doc__, version="0.5.1")
    if arguments["chart"]:
        chart_command(arguments)
    elif arguments["operation"] and (arguments["set"] or arguments["show"]):
        operations_command(arguments)
    elif arguments["ledger"]:
        ledger_command(arguments)
    elif arguments["post"]:
        post_command2(arguments)
    elif arguments["report"]:
        report_command(arguments)
    elif arguments["accounts"]:
        balances_command(arguments)
    elif arguments["account"]:
        print_account_balance(account_name=arguments["<account_name>"])
    elif arguments["assert"]:
        account_name, amount = arguments["<account_name>"], arguments["<amount>"]
        assert_account_balance(account_name, amount)
    elif arguments["erase"]:
        erase(arguments)
    else:
        sys.exit("Command not recognized. Use bx --help for reference.")


if __name__ == "__main__":
    main()
