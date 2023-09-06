"""
Usage:
  bx chart init
  bx chart add --assets <account_names>... 
  bx chart add --capital <account_names>... 
  bx chart add --liabilities <account_names>... 
  bx chart add --income <account_names>...
  bx chart add --expenses <account_names>... 
  bx chart offset <account_name> <contra_account_names>...
  bx chart adds --asset     <account_name> [--title <title>] [--code <code>] 
  bx chart adds --capital   <account_name> [--title <title>] [--code <code>]
  bx chart adds --liability <account_name> [--title <title>] [--code <code>]
  bx chart adds --income    <account_name> [--title <title>] [--code <code>]
  bx chart adds --expense   <account_name> [--title <title>] [--code <code>]
  bx chart set --retained-earnings <account_name>
  bx chart name <account_name> <title>
  bx chart code <account_name> <code>
  bx chart alias <name> <debit> <credit>
  bx chart show [--json]
  bx chart erase --force
  bx ledger open
  bx ledger post <debit> <credit> <amount>
  bx ledger close
  bx ledger show
  bx ledger erase --force
  bx report <account_name>
  bx report --trial-balance
  bx report --income-statement [--json] [--rich]
  bx report --balance-sheet [--json] [--rich]
  bx report --end-balances --json
  bx assert <account_name> <balance>
"""
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

# pylance: disable=import-error
# pylint: disable=import-error
from docopt import docopt  # type: ignore
from engine.base import AbacusError, Amount, Entry, AccountName
from engine.chart import Chart
from engine.closing import make_closing_entries
from engine.ledger import Ledger
from entries import CsvFile


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
        return "Added operation: " + name + " (debit " + debit + ", credit " + credit + ")."

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
        pass
    elif arguments["show"]:
        if arguments["--json"]:
            print(holder.chart.json())
        else:
            print_chart(holder.chart)
    elif arguments["erase"] and arguments["--force"]:
        chart_path.unlink(missing_ok=True)
        print("Deleted", chart_path)


def ledger_command(arguments: Dict, entries_path: Path, chart_path: Path):
    file = CsvFile(entries_path)
    if arguments["erase"] and arguments["--force"]:
        file.erase()
    elif arguments["open"]:
        file.touch()
        print("Created", entries_path)
    elif arguments["post"]:
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
    if arguments["<account_name>"]:
        entries = CsvFile(entries_path).yield_entries()
        ledger = Ledger.new(chart).post_many(entries)
        print_account_info(ledger, chart, arguments["<account_name>"])
    elif arguments["--trial-balance"]:
        entries = CsvFile(entries_path).yield_entries()
        ledger = Ledger.new(chart).post_many(entries)
        print(ledger.trial_balance(chart))
    elif arguments["--balance-sheet"]:
        entries = CsvFile(entries_path).yield_entries()
        ledger = Ledger.new(chart).post_many(entries)
        statement = ledger.balance_sheet(chart)
        if arguments["--json"]:
            print(statement.json())
        elif arguments["--rich"]:
            statement.print_rich(chart.names)
        else:
            print("Balance sheet")
            print(statement.view(chart.names))
    elif arguments["--income-statement"]:
        entries = CsvFile(entries_path).yield_entries()
        entries = filter_for_income_statement(entries, chart)
        ledger = Ledger.new(chart).post_many(entries)
        statement = ledger.income_statement(chart)
        if arguments["--json"]:
            print(statement.json())
        elif arguments["--rich"]:
            statement.print_rich(chart.names)
        else:
            print("Income statement")
            print(statement.view(chart.names))
    elif arguments["--end-balances"]:
        entries = CsvFile(entries_path).yield_entries()
        balances = Ledger.new(chart).post_many(entries).balances()
        if arguments["--json"]:
            print(json.dumps(balances))
        else:
            sys.exit("Use --json flag to print account end balances.")

def split_on_caps(account) -> str:
    import re
    return " ".join(re.findall('[A-Z][^A-Z]*', account.__class__.__name__))

def print_account_info(ledger, chart, account_name: str):
    account = ledger[account_name]
    print("Account:", chart.compose_name(account_name))
    print("   Type:", split_on_caps(account))
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
    print(f"Check passed for account {account_name}: account balance is {expected_amount}.")



def main():
    arguments = docopt(__doc__, version="0.5.1")
    if arguments["chart"]:
        chart_command(arguments, get_chart_path())
    elif arguments["ledger"]:
        ledger_command(arguments, get_entries_path(), get_chart_path())
    elif arguments["report"]:
        report_command(arguments, get_entries_path(), get_chart_path())
    elif arguments["assert"]:
        assert_command(arguments, get_entries_path(), get_chart_path())
    else:
        sys.exit("Command not recognized. Use bx --help for reference.")


if __name__ == "__main__":
    main()
