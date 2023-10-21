import os
import sys
from pathlib import Path
from typing import List, Dict
import json

import click

from abacus import AbacusError, Amount
from abacus.cli.chart_command import ChartCommand
from abacus.cli.ledger_command import LedgerCommand
from abacus.engine.base import AccountName
from abacus.engine.entries import File


def read_starting_balances(path: str) -> Dict:
    """Read starting balances from file *path*."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


@click.group()
def abacus():
    pass


@abacus.group()
def chart():
    """Define chart of accounts."""
    pass


@chart.command(name="init")
def init_chart():
    """Create chart of accounts file (chart.json) in current folder."""
    ChartCommand.init(path=get_chart_path()).echo()


def _add(account_name):
    try:
        path = get_chart_path()
        ChartCommand.read(path).promote(account_name).echo().write(path)
    except AbacusError as e:
        sys.exit(e)


@chart.command
@click.argument("account_name", type=str)
@click.option(
    "--title", type=str, required=False, help="Long account title."
)
def add(account_name: str, title: str):
    """Add account to chart.

    Examples:
        abacus add asset:cash --title "Cash and equivalents"
        abacus add expense:rent
        abacus add asset:ppe --title "Property, plant and equipment"
        abacus add contra:ppe:depreciation --title "Accumulated depreciation" """
    _add(account_name)
    if title:
       _name(account_name, title)



@chart.command
@click.argument("account_names", nargs=-1)
def add_many(account_names: List[AccountName]):
    """Add several accounts to chart."""
    for account_name in account_names:
        _add(account_name)


@chart.command()
@click.argument("account_name")
@click.option(
    "--title", type=str, required=False, help="Long account title."
)
def name(account_name, title):
    """Change account title."""
    _name(account_name, title)

def _name(account_name, title):
    path = get_chart_path()
    ChartCommand.read(path).set_name(account_name, title).echo().write(path)

@chart.command(name="show")
@click.option("--json", is_flag=True, help="Show chart as JSON.")
def show_chart(json):
    """Print chart of accounts."""
    # FIXME: need regular view without --json flag
    ChartCommand.read(path=get_chart_path()).show()


@chart.command(name="unlink")
@click.confirmation_option(
    prompt=f"Are you sure you want to permanently delete {get_chart_path()}?"
)
def unlink_chart():
    """Permanently delete chart of accounts file in current folder."""
    path = get_chart_path()
    File(path).erase()
    click.echo(f"Dropped {path}")


@abacus.group()
def ledger():
    """Post entries to ledger."""
    pass


@ledger.command(name="init")
@click.option("--file", type=click.Path(exists=True), help="JSON file with account starting balances.")
# add starting balances
def init_ledger(file):
    """Create ledger file (entries.linejson) in current folder."""
    path = get_entries_path()
    # maybe different message if not created
    ledger = LedgerCommand.init(path).echo()
    if file:
        starting_balances = read_starting_balances(file)
        chart = ChartCommand.read(path=get_chart_path()).chart
        ledger.post_starting_balances(chart, starting_balances).echo() 


def last(string):
    return string.split(":")[-1]


@ledger.command
@click.option("--debit", required=True, type=str, help="Debit account name.")
@click.option("--credit", required=True, type=str, help="Credit account name.")
@click.option("--amount", required=True, type=int, help="Transaction amount.")
def post(debit, credit, amount):
    """Post entry to ledger."""
    path=get_chart_path()
    ChartCommand.read(path).promote(debit).promote(credit).echo().write(path)  
    path=get_entries_path()
    LedgerCommand.read(path).post_entry(last(debit), last(credit), amount).echo()


@ledger.command
def close():
    """Close ledger at accounting period end."""
    # FIXME: allows to close accidentally twice
    chart = ChartCommand.read(path=get_chart_path()).chart
    LedgerCommand.read(path=get_entries_path()).post_closing_entries(chart).echo()


@ledger.command(name="show")
def show_ledger():
    """Print ledger."""
    LedgerCommand.read(path=get_entries_path()).show()


@ledger.command(name="unlink")
@click.confirmation_option(
    prompt=f"Are you sure you want to permanently delete {get_entries_path()}?"
)
def unlink_ledger():
    """Permanently delete ledger file in current folder."""
    path = get_entries_path()
    File(path).erase()
    click.echo(f"Dropped {path}")


@abacus.group()
def report():
    """Show reports."""
    pass


@report.command(name="trial-balance")
def trial_balance():
    """Show trial balance."""
    pass


@report.command(name="balance-sheet")
def balance_sheet():
    """Show balance sheet."""
    pass


@report.command(name="income-statement")
def income_statement():
    """Show income statement."""
    pass


@report.command(name="account-balances")
@click.option("--nonzero", is_flag=True, help="Omit accounts with zero balances.")
def account_balances():
    """Show account balances."""
    pass


@abacus.command()
@click.argument("account_name")
@click.option("--assert-balance", type=int, help="Verify account balance.")
def inspect(account_name: AccountName, assert_balance: Amount):
    """Show or check extra information."""
    pass


if __name__ == "__main__":
    abacus()
