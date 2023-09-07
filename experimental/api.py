"""
Usage:
  bx chart init
  bx chart add --assets <account_names>... 
  bx chart add --capital <account_names>... 
  bx chart add --liabilities <account_names>... 
  bx chart add --income <account_names>...
  bx chart add --expenses <account_names>... 
  bx chart offset <account_name> <contra_account_names>...
  bx chart name <account_name> <title>
  bx chart code <account_name> <code>
  bx chart set --asset     <account_name> [--title <title>] [--code <code>] 
  bx chart set --capital   <account_name> [--title <title>] [--code <code>]
  bx chart set --liability <account_name> [--title <title>] [--code <code>]
  bx chart set --income    <account_name> [--title <title>] [--code <code>]
  bx chart set --expense   <account_name> [--title <title>] [--code <code>]
  bx chart set --retained-earnings <account_name> [--title <title>] [--code <code>]
  bx chart alias --operation <name> --debit <debit> --credit <credit> [--requires <requires>]
  bx chart show [--json]
  bx chart erase --force
  bx ledger open [--start <file>]
  bx ledger post <debit> <credit> <amount>
  bx ledger post --operation (<operations> <amounts>)...
  bx ledger close
  bx ledger show
  bx ledger erase --force
  bx report --trial-balance
  bx report --income-statement [--json | --rich]
  bx report --balance-sheet [--json | --rich]
  bx accounts show <account_name> [--assert <balance>]
  bx accounts show --balances [--nonzero]
"""
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from docopt import docopt  # type: ignore
from engine.base import AbacusError, AccountName, Amount, Entry
from engine.chart import Chart
from engine.closing import make_closing_entries
from engine.ledger import Ledger
from entries import CsvFile
from engine.base import Pair


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.csv"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def init_chart(path: Path):
    """Write empty chart to *path* if does not file exist."""
    if not path.exists():
        ChartCommand(chart=Chart()).write(path)
    else:
        raise AbacusError


def print_chart(chart: Chart):
    def name(account_name):
        return chart.compose_name(account_name)

    for attribute in chart.five_types_of_accounts():
        account_names = getattr(chart, attribute)
        if account_names:
            print(attribute.capitalize() + ":")
            print(" ", ", ".join(map(name, account_names)))
    if chart.contra_accounts:
        print("Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("  -", contra_phrase(name(key), map(name, names)))
    print_re(chart)


def print_re(chart):
    print(
        "Retained earnings account:",
        chart.compose_name(chart.retained_earnings_account),
    )


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


@dataclass
class ChartCommand:
    chart: Chart

    @classmethod
    def read(cls, path: Path):
        return ChartCommand(chart=Chart.parse_file(path))

    def write(self, path: Path):
        content = self.chart.json(indent=4, ensure_ascii=True)
        Path(path).write_text(content, encoding="utf-8")

    def set_retained_earnings(self, account_name):
        """Set name of null account (override default name).

        Command:
        ```
        bx set --retained-earnings <account_name>
        ```
        """
        self.chart.retained_earnings_account = account_name
        return self

    def set_null_account(self, account_name):
        """Set name of null account (override default name).

        Command:
        ```
        bx set --null-account <account_name>
        ```
        """

    def set_isa(self, account_name):
        """Set name of income summary account (override default name).

        Command:
        ```
        bx set --income-summary-account <account_name>
        ```
        """

    def _add(self, attribute: str, account_names: List[str]):
        setattr(self.chart, attribute, getattr(self.chart, attribute) + account_names)

    def add_assets(self, account_names: List[str]):
        self._add("assets", account_names)
        return self

    def add_capital(self, account_names):
        # add account_names to 'equity' attribute
        self._add("equity", account_names)
        return self

    def add_liabilities(self, account_names):
        self._add("liabilities", account_names)
        return self

    def add_income(self, account_names):
        self._add("income", account_names)
        return self

    def add_expenses(self, account_names):
        self._add("expenses", account_names)
        return self

    def offset(self, account_name, contra_account_names) -> str:
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
        if len(contra_account_names) > 1:
            text = "Added countra accounts: "
        else:
            text = "Added contra account: "
        return text + contra_phrase(account_name, contra_account_names) + "."

    def alias(self, name: str, debit: AccountName, credit: AccountName):
        self.chart.add_operation(name, debit, credit)
        return f"Added operation {name}, where debit is {debit} and credit is {credit}."

    def set_name(self, account_name, title) -> str:
        self.chart.set_name(account_name, title)
        return "Added account title: " + self.chart.compose_name(account_name) + "."


def chart_command(arguments: Dict, chart_path: Path):
    if arguments["init"]:
        try:
            init_chart(chart_path)
            print("Created", chart_path)
            sys.exit(0)
        except AbacusError:
            sys.exit(f"File already exists: {chart_path}")
    # load chart file
    try:
        holder = ChartCommand.read(chart_path)
    except FileNotFoundError:
        sys.exit(
            f"File not found (expected {chart_path}).\nUse `bx chart init` to create chart file."
        )
    # commands below assume chart file exists
    if arguments["set"] and arguments["--retained-earnings"]:
        holder.set_retained_earnings(arguments["<account_name>"])
        holder.write(chart_path)
        print_re(holder.chart)
    elif arguments["add"]:
        account_names = arguments["<account_names>"]
        if arguments["--assets"]:
            holder.add_assets(account_names)
        elif arguments["--capital"]:
            holder.add_capital(account_names)
        elif arguments["--liabilities"]:
            holder.add_liabilities(account_names)
        elif arguments["--income"]:
            holder.add_income(account_names)
        elif arguments["--expenses"]:
            holder.add_expenses(account_names)
        holder.write(chart_path)
        print("Added accounts to chart:", account_names)
    elif arguments["offset"]:
        msg = holder.offset(
            arguments["<account_name>"], arguments["<contra_account_names>"]
        )
        holder.write(chart_path)
        print(msg)
    elif arguments["name"]:
        msg = holder.set_name(arguments["<account_name>"], arguments["<title>"])
        holder.write(chart_path)
        print(msg)
    elif arguments["code"]:
        pass
    elif arguments["alias"]:
        msg = holder.alias(
            arguments["<name>"], arguments["<debit>"], arguments["<credit>"]
        )
        holder.write(chart_path)
        print(msg)
    elif arguments["show"]:
        if arguments["--json"]:
            print(holder.chart.json())
        else:
            print_chart(holder.chart)
    elif arguments["erase"] and arguments["--force"]:
        chart_path.unlink(missing_ok=True)
        print("Deleted", chart_path)


from engine.ledger import to_multiple_entry


def ledger_command(arguments: Dict, entries_path: Path, chart_path: Path):
    file = CsvFile(entries_path)
    chart = Chart.parse_file(chart_path)
    if arguments["erase"] and arguments["--force"]:
        file.erase()
    elif arguments["open"]:
        file.touch()
        print("Created", entries_path)
        if arguments["--start"]:
            balances = read_starting_balances(arguments["<file>"])
            print("Starting balances:", balances)
            me = to_multiple_entry(Ledger.new(chart), balances)
            entries = me.entries(chart.null_account)
            x = Ledger.new(chart).post_many(entries)[chart.null_account].balance()
            print("Balance of null account is", x, "(expected balance is 0).")
            assert x == 0
            file.append_many(entries)
            print("Added entries", entries)
    elif arguments["post"]:
        if arguments["--operation"]:
            operations = arguments["<operations>"]
            amounts = arguments["<amounts>"]
            for operation, amount in zip(operations, amounts):
                debit, credit = chart.operations[operation]
                entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
                file.append(entry)
                print("Posted entry:", entry)
        else:
            entry = Entry(
                debit=arguments["<debit>"],
                credit=arguments["<credit>"],
                amount=Amount(arguments["<amount>"]),
            )
            file.append(entry)
            print("Posted entry:", entry)
    elif arguments["close"]:
        chart = Chart.parse_file(chart_path)
        ledger = Ledger.new(chart)
        ledger.post_many(entries=file.yield_entries())
        closing_entries = make_closing_entries(chart, ledger).all()
        file.append_many(entries=closing_entries)
        print("Added closing entries:", closing_entries)
    elif arguments["show"]:
        for entry in file.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep="\t")


def touches_isa(chart: Chart, entry: Entry) -> bool:
    """True if entry touches income summary account."""
    isa = chart.income_summary_account
    return (entry.debit == isa) or (entry.credit == isa)


def filter_for_income_statement(entries: List[Entry], chart: Chart):
    """Filter entries that do not close income accounts."""

    def not_touches_isa(entry):
        return not touches_isa(chart, entry)

    return filter(not_touches_isa, entries)


def report_command(arguments: Dict, entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    entries = CsvFile(entries_path).yield_entries()
    ledger = Ledger.new(chart)
    if arguments["--trial-balance"]:
        ledger.post_many(entries)
        print(ledger.trial_balance(chart))
    elif arguments["--balance-sheet"]:
        ledger.post_many(entries)
        statement = ledger.balance_sheet(chart)
        if arguments["--json"]:
            print(statement.json())
        elif arguments["--rich"]:
            statement.print_rich(chart.names)
        else:
            print("Balance sheet")
            print(statement.view(chart.names))
    elif arguments["--income-statement"]:
        entries = filter_for_income_statement(entries, chart)
        ledger.post_many(entries)
        statement = ledger.income_statement(chart)
        if arguments["--json"]:
            print(statement.json())
        elif arguments["--rich"]:
            statement.print_rich(chart.names)
        else:
            print("Income statement")
            print(statement.view(chart.names))


def print_account_info(ledger, chart, account_name: str):
    account = ledger[account_name]
    print("Account:", chart.compose_name(account_name))
    print("   Type:", account.split_on_caps())
    print(" Debits:", account.debits)
    print("Credits:", account.credits)
    print("Balance:", account.balance())


def assert_command(arguments, entries_path, chart_path):
    chart = Chart.parse_file(chart_path)
    entries = CsvFile(entries_path).yield_entries()
    ledger = Ledger.new(chart).post_many(entries)
    assert_account_balance(ledger, arguments["<account_name>"], arguments["<balance>"])


def assert_account_balance(ledger, account_name: str, assert_amount: str):
    amount = ledger[account_name].balance()
    expected_amount = Amount(assert_amount)
    if amount != expected_amount:
        sys.exit(
            f"Check failed for {account_name}: expected balance is {expected_amount}, got {amount}."
        )
    print(
        f"Check passed for account {account_name}: account balance is {expected_amount}."
    )


def accounts_command(arguments, entries_path, chart_path):
    """
    bx accounts show <account_name> [--assert <balance>]
    bx accounts show --balances [--nonzero]
    """
    chart = Chart.parse_file(chart_path)
    entries = CsvFile(entries_path).yield_entries()
    ledger = Ledger.new(chart).post_many(entries)
    if account_name := arguments["<account_name>"]:
        if arguments["--assert"]:
            assert_account_balance(ledger, account_name, arguments["<balance>"])
        else:
            print_account_info(ledger, chart, account_name)
    elif arguments["--balances"]:
        # this command always returns a json, there is no --json flag
        balances = ledger.balances()
        if arguments["--nonzero"]:
            balances = {k: v for k, v in balances.items() if v}
        print(json.dumps(balances))

def main():
    arguments = docopt(__doc__, version="0.5.1")
    if arguments["chart"]:
        chart_command(arguments, get_chart_path())
    elif arguments["ledger"]:
        ledger_command(arguments, get_entries_path(), get_chart_path())
    elif arguments["report"]:
        report_command(arguments, get_entries_path(), get_chart_path())
    elif arguments["accounts"]:
        accounts_command(arguments, get_entries_path(), get_chart_path())
    else:
        sys.exit("Command not recognized. Use bx --help for reference.")


def read_starting_balances(path: str) -> Dict:
    """Read starting balances from file *path*."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
