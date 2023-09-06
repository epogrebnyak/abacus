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
  bx chart show [--json]
  bx chart erase --force
"""
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from docopt import docopt
from engine.base import AbacusError, AccountName
from engine.chart import Chart
from engine.ledger import Ledger


def cwd() -> Path:
    return Path(os.getcwd())


def chart_path() -> Path:
    return cwd() / "chart.json"


def entries_path() -> Path:
    return cwd() / "entries.csv"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


# def write_json(path, content):
#     return Path(path).write_text(
#         json.dumps(content, ensure_ascii=True, indent=4), encoding="utf-8"
#     )


def init_chart(path: Path):
    """Write empty chart to *path* if does not file exist."""
    if not path.exists():
        ChartCommand(chart=Chart()).write(path)
    else:
        raise AbacusError


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
        pass

    def _add(self, attribute: str, account_names: List[str]):
        attributes = ["assets", "equity", "liabilities", "income", "expenses"]
        try:
            setattr(
                self.chart, attribute, getattr(self.chart, attribute) + account_names
            )
        except AttributeError:
            raise AbacusError(
                f"Flag must be one of {attributes}, provided: {attribute}"
            )

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


    def name(self, account_name, title) -> str:
        self.chart.set_name(account_name, title)
        return "Added account title: " + name_account(self.chart, account_name) + "."


    def show(self, account: AccountName | None = None):
        pass

    def validate(self):
        pass


def name_account(chart, account_name):
    return account_name + " (" + chart.get_name(account_name) + ")"


def print_chart(chart: Chart):
    def name(account_name):
        return name_account(chart, account_name)

    for attribute in chart.five_types_of_accounts():
        account_names = getattr(chart, attribute)
        if account_names:
            print(attribute.capitalize() + ":")
            print(" ", ", ".join(map(name, account_names)))
    if chart.contra_accounts:
        print("Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("  -", contra_phrase(name(key), map(name, names)))
    print("Retained earnings account:\n  ", name(chart.retained_earnings_account))


def chart_command(arguments: Dict, chart_path: Path):
    if arguments["init"]:
        try:
            init_chart(chart_path)
            print("Created chart file", chart_path)
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
    if arguments["set"] and arguments["--retained-earnings"]:
        holder.set_retained_earnings(arguments["<account_name>"]).save(chart_path)
        print("Retained earnings account name was set to:", arguments["<account_name>"])
        sys.exit(0)
    if arguments["add"]:
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
        sys.exit(0)
    if arguments["offset"]:
        # modify and save
        msg = holder.offset(arguments["<account_name>"], arguments["<contra_account_names>"])
        holder.write(chart_path)
        # notify
        print(msg)
        sys.exit(0)
    if arguments["name"]:
        msg = holder.name(arguments["<account_name>"], arguments["<title>"])
        holder.write(chart_path)
        print(msg)
        sys.exit(0)
    if arguments["show"]:
        if arguments["--json"]:
            print(holder.chart.json())
        else:
            print_chart(holder.chart)
        sys.exit(0)
    if arguments["erase"] and arguments["--force"]:
        chart_path.unlink(missing_ok=True)
        print("Deleted", chart_path)
        sys.exit(0)


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


class LedgerCommand:
    ledger: Ledger

    def start(self, filename: str | None = None):
        pass

    def post(self):
        pass

    def close(self):
        pass


class ReportCommand:
    def trial_balance(self):
        pass

    def balance_sheet(self, json: bool):
        pass

    def income_statement(self, json: bool):
        pass

    def end_balances(self, json: bool):
        pass


def main():
    arguments = docopt(__doc__, version="0.5.1")
    if arguments["chart"]:
        chart_command(arguments, chart_path())
        # elif arguments["ledger"]:
        #     ledger_command(arguments)
        # elif arguments["report"]:
        #     report_command(arguments)
        # else:
        sys.exit("Command not recognized. Use bx --help for reference.")


if __name__ == "__main__":
    main()
