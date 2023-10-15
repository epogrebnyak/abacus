"""
Usage:
  bx chart init
  bx chart add --asset     <account_name> [(--title <title>)] [(--code <code>)] 
  bx chart add --capital   <account_name> [(--title <title>)] [(--code <code>)] 
  bx chart add --liability <account_name> [(--title <title>)] [(--code <code>)] 
  bx chart add --income    <account_name> [(--title <title>)] [(--code <code>)] 
  bx chart add --expense   <account_name> [(--title <title>)] [(--code <code>)] 
  bx chart offset <account_name> <contra_account_names>...
  bx chart set <account_name> [(--title <title>)] [(--code <code>)]
  bx chart set --retained-earnings <account_name> [(--title <title>)] [(--code <code>)]
  bx chart set --income-summary-account <account_name> [(--title <title>)] [(--code <code>)]
  bx chart set --null-account <account_name> [(--title <title>)] [(--code <code>)]
  bx chart alias --operation <name> --debit <debit> --credit <credit> [(--requires <requires>)]
  bx chart show [--json]
  bx chart erase --force
  bx ledger init [<file>]
  bx [ledger] post operation (<operations> <amounts>)...  [(--title <title>)]
  bx [ledger] post entry --debit <debit> --credit <credit> --amount <amount> [(--title <title>)] [--adjust | --after-close]
  bx ledger close
  bx ledger show
  bx ledger erase --force
  bx report --trial-balance
  bx report --income-statement [--json | --rich]
  bx report --balance-sheet [--json | --rich]
  bx account <account_name>
  bx assert <account_name> <balance>
  bx balances [--nonzero]
"""
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from docopt import docopt  # type: ignore

from abacus.engine.accounts import CreditAccount, DebitAccount
from abacus.engine.base import AbacusError, AccountName, Amount, Entry
from abacus.engine.chart import Chart
from abacus.engine.closing import make_closing_entries
from abacus.engine.entries import CsvFile
from abacus.engine.ledger import Ledger


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
        return chart.namer.compose_name(account_name)

    print("Accounts:")
    for attribute in chart.five_types_of_accounts():
        account_names = getattr(chart, attribute)
        if account_names:
            print(attribute.capitalize() + ":", ", ".join(map(name, account_names)))
    if chart.contra_accounts:
        print("Contra accounts:")
        for key, names in chart.contra_accounts.items():
            print("  -", contra_phrase(name(key), map(name, names)))
    print_re(chart)
    if chart.operations:
        print("Operation aliases:")
        for key, (debit, credit) in chart.operations.items():
            print("  -", key, f"(debit is {debit}, credit is {credit})")


def print_re(chart):
    print(
        "Retained earnings account:",
        chart.namer.compose_name(chart.retained_earnings_account) + ".",
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
        self.chart.null_account = account_name
        return self

    def set_isa(self, account_name):
        """Set name of income summary account (override default name).

        Command:
        ```
        bx set --income-summary-account <account_name>
        ```
        """
        self.chart.income_summary_account = account_name
        return self

    def _add(self, attribute: str, account_name: str):
        new_list = getattr(self.chart, attribute) + [account_name]
        setattr(self.chart, attribute, new_list)
        return self

    def add_asset(self, account_name: str):
        return self._add("assets", account_name)

    def add_capital(self, account_name: str):
        # will adding account_name to 'equity' attribute
        return self._add("equity", account_name)

    def add_liability(self, account_name: str):
        return self._add("liabilities", account_name)

    def add_income(self, account_name: str):
        return self._add("income", account_name)

    def add_expense(self, account_name: str):
        return self._add("expenses", account_name)

    def offset(self, account_name, contra_account_names) -> str:
        for contra_account_name in contra_account_names:
            self.chart.offset(account_name, contra_account_name)
        if len(contra_account_names) > 1:
            text = "Added contra accounts: "
        else:
            text = "Added contra account: "
        return text + contra_phrase(account_name, contra_account_names) + "."

    def alias(self, name: str, debit: AccountName, credit: AccountName):
        self.chart.add_operation(name, debit, credit)
        return f"Added operation: {name} (debit is {debit}, credit is {credit})."

    def set_name(self, account_name, title) -> str:
        self.chart.set_name(account_name, title)
        return (
            "Added account title: " + self.chart.namer.compose_name(account_name) + "."
        )

    def set_code(self, account_name, code: str) -> str:
        self.chart.set_code(account_name, code)
        return f"Set code {code} for account {account_name}."


def chart_command(arguments: Dict, chart_path: Path):
    if arguments["init"]:
        try:
            init_chart(chart_path)
            print("Created", chart_path)
            sys.exit(0)
        except AbacusError:
            sys.exit(f"File already exists: {chart_path}")
    if arguments["erase"] and arguments["--force"]:
        if chart_path.exists():
            chart_path.unlink(missing_ok=True)
            print("Deleted", chart_path)
        else:
            print("File not found:", chart_path)
        sys.exit(0)
    # load chart file
    try:
        holder = ChartCommand.read(chart_path)
    except FileNotFoundError:
        sys.exit(
            f"File not found (expected {chart_path}).\nUse `bx chart init` to create chart file."
        )
    # commands below assume chart file exists
    account_name = arguments["<account_name>"]
    if arguments["set"] or arguments["add"]:
        if arguments["--title"]:
            title = arguments["<title>"]
            msg = holder.set_name(account_name, title)
            print(msg)
            holder.write(chart_path)
        if arguments["--code"]:
            code = arguments["<code>"]
            if not code:
                raise ValueError(f"Code must be provided, got {code} in {arguments}.")
            msg = holder.set_code(account_name, code)
            print(msg)
            holder.write(chart_path)
        # set
        if arguments["--retained-earnings"]:
            holder.set_retained_earnings(account_name)
            print_re(holder.chart)
        elif arguments["--income-summary-account"]:
            holder.set_isa(account_name)
        elif arguments["--null-account"]:
            holder.set_null_account(account_name)
        # add
        if arguments["--asset"]:
            holder.add_asset(account_name)
        elif arguments["--capital"]:
            holder.add_capital(account_name)
        elif arguments["--liability"]:
            holder.add_liability(account_name)
        elif arguments["--income"]:
            holder.add_income(account_name)
        elif arguments["--expense"]:
            holder.add_expense(account_name)
        holder.write(chart_path)
        print("Added account to chart:", account_name + ".")
    elif arguments["offset"]:
        msg = holder.offset(
            arguments["<account_name>"], arguments["<contra_account_names>"]
        )
        print(msg)
        holder.write(chart_path)
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


@dataclass
class LedgerCommand:
    chart: Chart
    csv_file: CsvFile

    def show(self):
        for entry in self.csv_file.yield_entries():
            print(entry.debit, entry.credit, entry.amount, sep="\t")

    def post_starting_balances(self, starting_balances_dict: Dict):
        self.chart.ledger(starting_balances_dict)  # check that all accounts are present
        me = self.chart.ledger().make_multiple_entry(starting_balances_dict)
        entries = me.entries(self.chart.null_account)
        self.csv_file.append_many(entries)
        for entry in entries:
            print("Posted entry:", entry)

    def post_operations(self, operations: List[str], amounts: List[str]):
        entries = self.chart.make_entries_for_operations(operations, amounts)
        self.csv_file.append_many(entries)
        for entry in entries:
            print("Posted entry:", entry)

    def post_closing_entries(self):
        ledger = Ledger.new(self.chart)
        ledger.post_many(entries=self.csv_file.yield_entries())
        closing_entries = make_closing_entries(self.chart, ledger).all()
        self.csv_file.append_many(entries=closing_entries)
        print("Added closing entries:")
        for entry in closing_entries:
            print(" ", entry)

    def post_entry(self, debit: str, credit: str, amount: str):
        try:
            entry = Entry(debit=debit, credit=credit, amount=Amount(amount))
        except TypeError:
            raise AbacusError(f"Invalid entry: {debit}, {credit}, {amount}.")
        self.csv_file.append(entry)
        print("Posted entry:", entry)


def ledger_command(arguments: Dict, entries_path: Path, chart_path: Path):
    csv_file = CsvFile(entries_path)
    if arguments["erase"] and arguments["--force"]:
        csv_file.erase()
        sys.exit(0)
    chart = Chart.parse_file(chart_path)
    holder = LedgerCommand(chart=chart, csv_file=csv_file)
    if arguments["init"]:
        csv_file.touch()
        print("Created", entries_path)
        if start_balances_file := arguments["<file>"]:
            balances = read_starting_balances(start_balances_file)
            print("Starting balances:", balances)
            holder.post_starting_balances(balances)
    elif arguments["post"] and arguments["entry"]:
        holder.post_entry(
            debit=arguments["<debit>"],
            credit=arguments["<credit>"],
            amount=arguments["<amount>"],
        )
    elif arguments["post"] and arguments["operation"]:
        holder.post_operations(arguments["<operations>"], arguments["<amounts>"])
    elif arguments["close"]:
        holder.post_closing_entries()
    elif arguments["show"]:
        holder.show()


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


def side(ledger, account_name):
    match ledger[account_name]:
        case DebitAccount(_, _):
            return "debit"
        case CreditAccount(_, _):
            return "credit"
        case _:
            raise TypeError(ledger[account_name].__class__.__name__)


def print_account_info(ledger, chart, account_name: str):
    account = ledger[account_name]
    print("     Account:", chart.namer[account_name])
    print("  Short name:", account_name)
    print("   Long name:", chart.namer.compose_name_long(account_name))
    print("        Code:", chart.codes.get(account_name, "not assigned"))
    print("        Type:", account.split_on_caps())
    print("      Debits:", str(account.debits) + ",", "total", sum(account.debits))
    print("     Credits:", str(account.credits) + ",", "total", sum(account.credits))
    print("     Balance:", account.balance())
    print("Balance side:", side(ledger, account_name).capitalize())


def assert_command(arguments, entries_path, chart_path):
    chart = Chart.parse_file(chart_path)
    entries = CsvFile(entries_path).yield_entries()
    ledger = Ledger.new(chart).post_many(entries)
    assert_account_balance(ledger, arguments["<account_name>"], arguments["<balance>"])


def assert_account_balance(ledger, account_name: str, assert_amount: str):
    amount = ledger[account_name].balance()
    expected_amount = Amount(assert_amount)
    msg_ok = f"Check passed for account {account_name}, account balance is {expected_amount} as expected."
    msg_fail = f"Check failed for {account_name}, expected balance is {expected_amount}, got {amount}."
    if amount != expected_amount:
        sys.exit(msg_fail)
    print(msg_ok)


def account_command(arguments, entries_path, chart_path):
    """
    bx account <account_name>
    """
    chart = Chart.parse_file(chart_path)
    ledger = process_full_ledger(chart_path, entries_path)
    account_name = arguments["<account_name>"]
    print_account_info(ledger, chart, account_name)


def process_full_ledger(chart_path: Path, entries_path: Path) -> Ledger:
    chart = Chart.parse_file(chart_path)
    entries = CsvFile(entries_path).yield_entries()
    return Ledger.new(chart).post_many(entries)


def show_balances_command(arguments, entries_path, chart_path):
    """
    bx balances [--nonzero]
    """
    # this command always returns a json, there is no --json flag
    ledger = process_full_ledger(chart_path, entries_path)
    balances = ledger.balances()
    if arguments["--nonzero"]:
        balances = ledger.nonzero_balances()
    print(json.dumps(balances))


def main():
    entries_path = get_entries_path()
    chart_path = get_chart_path()
    arguments = docopt(__doc__, version="0.7.0")
    if arguments["chart"]:
        chart_command(arguments, chart_path)
    elif arguments["ledger"]:
        ledger_command(arguments, entries_path, chart_path)
    elif arguments["report"]:
        report_command(arguments, entries_path, chart_path)
    elif arguments["account"]:
        account_command(arguments, entries_path, chart_path)
    elif arguments["assert"]:
        assert_command(arguments, entries_path, chart_path)
    elif arguments["balances"]:
        show_balances_command(arguments, entries_path, chart_path)
    else:
        sys.exit("Command not recognized. Use bx --help for reference.")


def read_starting_balances(path: str) -> Dict:
    """Read starting balances from file *path*."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
