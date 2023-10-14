from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict

from abacus import AbacusError, Amount, Chart, Entry, Ledger
from abacus.engine.base import AccountName
from abacus.engine.entries import CsvFile


def contra_phrase(account_name, contra_account_names):
    return account_name + " is offset by " + ", ".join(contra_account_names)


def init_chart(path: Path) -> None:
    """Write empty chart to *path* if does not file exist."""
    if not path.exists():
        ChartCommand.new().write(path)
    else:
        raise AbacusError


@dataclass
class Lоgger:
    """Logger will hold string notifiaction about last action taken"""

    message: str = ""

    def log(self, string: str):
        self.message = string


class RegularAccount(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


def flag_to_account_type(flag: str) -> RegularAccount:
    return RegularAccount(flag.upper())


@dataclass
class ChartCommand:
    chart: Chart
    logger: Lоgger = Lоgger()

    def echo(self):
        print(self.logger.message)
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    @classmethod
    def new(cls) -> "ChartCommand":
        return ChartCommand(chart=Chart())

    @classmethod
    def read(cls, path: Path) -> "ChartCommand":
        return ChartCommand(chart=Chart.parse_file(path))

    def write(self, path: Path) -> "ChartCommand":
        content = self.chart.json(indent=4, ensure_ascii=True)
        Path(path).write_text(content, encoding="utf-8")
        self.log(f"Wrote chart file: {path}")
        return self

    def set_retained_earnings(self, account_name) -> "ChartCommand":
        """Оverride default name of retained earnings account."""
        self.chart.retained_earnings_account = account_name
        return self

    def set_null_account(self, account_name) -> "ChartCommand":
        """Оverride default name of null account."""
        self.chart.null_account = account_name
        return self

    def set_isa(self, account_name) -> "ChartCommand":
        """Оverride default name of income summary account."""
        self.chart.income_summary_account = account_name
        return self

    def add_account_by_prefix(self, prefix: str, account_name: str) -> "ChartCommand":
        """Add account to chart by prefix."""
        if prefix in ["asset", "assets"]:
            self.add_asset(account_name)
        elif prefix in ["liability", "liabilities"]:
            self.add_liability(account_name)
        elif prefix in ["capital", "equity"]:
            self.add_capital(account_name)
        elif prefix in ["expense", "expenses"]:
            self.add_expense(account_name)
        elif prefix in ["income"]:
            self.add_income(account_name)
        else:
            raise AbacusError(f"Invalid account prefix: {prefix}")
        return self

    def _add(self, attribute: str, account_name: str) -> "ChartCommand":
        """Generic metod to add account of *atrribute* type to chart.
        Attribute in any of ['assets', 'liabilities', 'equity', 'income', 'expenses'].
        """
        account_names = getattr(self.chart, attribute)
        if account_name not in account_names:
            setattr(self.chart, attribute, account_names + [account_name])
        return self

    def add_asset(self, account_name: str):
        return self._add("assets", account_name)

    def add_capital(self, account_name: str):
        """Add *account_name* to 'equity' attribute of the chart."""
        return self._add("equity", account_name)

    def add_liability(self, account_name: str):
        return self._add("liabilities", account_name)

    def add_income(self, account_name: str):
        return self._add("income", account_name)

    def add_expense(self, account_name: str):
        return self._add("expenses", account_name)

    def offset(self, account_name, contra_account_names) -> "ChartCommand":
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
        # logging
        ending = "s" if len(contra_account_names) > 1 else ""
        text = f"Added contra account{ending}:"
        self.log(text + " " + contra_phrase(account_name, contra_account_names) + ".")
        return self

    def alias(self, name: str, debit: AccountName, credit: AccountName):
        self.chart.add_operation(name, debit, credit)
        self.log(f"Added operation: {name} (debit is {debit}, credit is {credit}).")
        return self

    def set_name(self, account_name, title) -> "ChartCommand":
        self.chart.set_name(account_name, title)
        self.log(f"Added account title: {self.chart.namer.compose_name(account_name)}.")
        return self

    def set_code(self, account_name, code: str) -> "ChartCommand":
        self.chart.set_code(account_name, code)
        self.log(f"Set code {code} for account {account_name}.")
        return self

    def promote(self, string: str) -> "ChartCommand":
        parts = string.split(":")
        match len(parts):
            case 1:
                if not self.chart.viewer.contains(parts[0]):
                    raise AbacusError(
                        f"Account name must be defined before use: {parts[0]}"
                    )
            case 2:
                self.add_account_by_prefix(parts[0], parts[1])
            case 3:
                if parts[0] == "contra":
                    self.offset(parts[1], [parts[2]])
                else:
                    raise AbacusError(f"Wrong account name format: {string}")
            case _:
                raise AbacusError(f"Too many colons in account name: {string}")
        return self


@dataclass
class LedgerCommand:
    csv_file: CsvFile
    logger: Lоgger = Lоgger()

    def echo(self):
        print(self.logger.message)
        return self

    def log(self, message):
        self.logger.log(message)
        return self

    @classmethod
    def start_ledger(cls, path) -> "LedgerCommand":
        csv_file = CsvFile(path).touch()
        return LedgerCommand(csv_file).log(f"Wrote ledger file: {path}")

    @classmethod
    def read(cls, path: Path) -> "LedgerCommand":
        return LedgerCommand(csv_file=CsvFile(path))

    def erase(self) -> "LedgerCommand":
        self.csv_file.erase()

    def show(self, sep=","):
        for entry in self.csv_file.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep=sep)

    def post_starting_balances(self, starting_balances_dict: Dict):
        pass

    def post_closing_entries(self, chart):
        ledger = Ledger.new(chart)
        ledger.post_many(entries=self.csv_file.yield_entries())
        closing_entries = ledger.closing_entries(chart)
        self.csv_file.append_many(entries=closing_entries)
        print("Posted closing entries:")
        for entry in closing_entries:
            print(" ", entry)

    def post_entry(self, debit: str, credit: str, amount: str):
        try:
            entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        except TypeError:
            raise AbacusError(f"Invalid entry: {debit}, {credit}, {amount}.")
        self.csv_file.append(entry)
        print("Posted entry:", entry)


def report_command(arguments: Dict, entries_path: Path, chart_path: Path):
    chart = Chart.parse_file(chart_path)
    store = CsvFile(entries_path)
    entries = store.yield_entries()
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
        entries = store.yield_entries_for_income_statement(chart)
        ledger.post_many(entries)
        statement = ledger.income_statement(chart)
        if arguments["--json"]:
            print(statement.json())
        elif arguments["--rich"]:
            statement.print_rich(chart.names)
        else:
            print("Income statement")
            print(statement.view(chart.names))
