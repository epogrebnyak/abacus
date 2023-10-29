import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import click

from abacus import AbacusError, Chart
from abacus.cli.chart_command import ChartCommand, ChartPath
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


@chart.command(name="init")
def init_chart():
    """Create chart of accounts file (chart.json) in current folder."""
    ChartPath(path=get_chart_path()).init().echo()


def promote(account_name):
    """Safe add account to chart."""
    try:
        ChartPath(path=get_chart_path()).read().promote(account_name).echo().write()
    except AbacusError as e:
        sys.exit(e)


@chart.command
@click.argument("account_name", type=str)
@click.option("--title", type=str, required=False, help="Long account title.")
def add(account_name: str, title: str):
    """Add account to chart with optional title.

    Examples:
        abacus add asset:cash --title "Cash and equivalents"
        abacus add expense:rent
        abacus add asset:ppe --title "Property, plant and equipment"
        abacus add contra:ppe:depreciation --title "Accumulated depreciation" """
    _add(account_name)
    if title:
        _name(last(account_name), title)


@chart.command
@click.argument("account_names", nargs=-1)
def add_many(account_names: List[AccountName]):
    """Add several accounts to chart."""
    for account_name in account_names:
        _add(account_name)


@chart.command()
@click.argument("account_name")
@click.option("--title", type=str, required=False, help="Account title.")
def name(account_name, title):
    """Change account title."""
    _name(account_name, title)


@chart.command(name="set")
@click.option("--re", type=str, required=False, help="Retained earnings account name.")
@click.option("--null", type=str, required=False, help="Null account name.")
@click.option("--isa", type=str, required=False, help="Income summary account name.")
def set_special_accounts(re, null, isa):
    """Change default names of retained earnings, income summary or null account."""
    path = get_chart_path()
    command = ChartCommand.read(path)
    if re:
        command.set_retained_earnings(re).echo().write(path)
    if null:
        command.set_null_account(null).echo().write(path)
    if isa:
        command.set_isa(isa).echo().write(path)


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
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="JSON file with account starting balances.",
)
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
    path = get_chart_path()
    ChartCommand.read(path).promote(debit).promote(credit).echo().write(path)
    path = get_entries_path()
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


@abacus.group
def report():
    """Show reports."""
    pass


@report.command(name="trial-balance")
def trial_balance():
    """Show trial balance."""
    from abacus.cli.report_command import trial_balance

    click.echo(trial_balance(get_entries_path(), get_chart_path()))


def echo_statement(statement, chart, plain, json, rich):
    match sum(1 for x in [plain, json, rich] if x):
        case 0:
            plain = True
        case 1:
            pass
        case _:
            sys.exit("Choose one of --plain, --json or --rich.")
    if json:
        click.echo(statement.json())
    elif rich:
        click.echo(statement.print_rich(chart.names))
    elif plain:
        click.echo(statement.view(chart.names))


@report.command(name="balance-sheet")
@click.option(
    "--plain",
    is_flag=True,
    help="Plain text output [default].",
)
@click.option(
    "--rich",
    is_flag=True,
    help="Rich text output.",
)
@click.option("--json", is_flag=True, help="Format output as JSON.")
def balance_sheet(plain, rich, json):
    """Show balance sheet."""
    from abacus.cli.report_command import balance_sheet

    statement = balance_sheet(get_entries_path(), get_chart_path())
    chart = ChartCommand.read(path=get_chart_path()).chart
    echo_statement(statement, chart, plain, json, rich)


@report.command(name="income-statement")
@click.option(
    "--plain",
    is_flag=True,
    help="Plain text output [default].",
)
@click.option(
    "--rich",
    is_flag=True,
    help="Rich text output.",
)
@click.option("--json", is_flag=True, help="Format output as JSON.")
def income_statement(plain, rich, json):
    """Show income statement."""
    from abacus.cli.report_command import income_statement

    statement = income_statement(get_entries_path(), get_chart_path())
    chart = ChartCommand.read(path=get_chart_path()).chart
    echo_statement(statement, chart, plain, json, rich)


@report.command(name="account-balances")
@click.option("--nonzero", is_flag=True, help="Omit accounts with zero balances.")
def account_balances(nonzero):
    """Show account balances."""
    from abacus.cli.report_command import account_balances

    balances = account_balances(
        entries_path=get_entries_path(), chart_path=get_chart_path(), nonzero=nonzero
    )
    click.echo(jsonify(balances))


def jsonify(x):
    return json.dumps(x, indent=4, sort_keys=True, ensure_ascii=False)


@abacus.command()
@click.argument("account_name")
@click.option("--assert-balance", type=int, help="Verify account balance.")
def inspect(account_name: str, assert_balance: int):
    """Show or check extra information."""
    from abacus.cli.inspect_command import assert_account_balance, print_account_info
    from abacus.cli.report_command import current_ledger

    ledger = current_ledger(
        chart_path=get_chart_path(), entries_path=get_entries_path()
    )
    if assert_balance or assert_balance == 0:
        print("Checking balance...")
        assert_account_balance(ledger, account_name, assert_balance)
    else:
        print_account_info(ledger, get_chart(), account_name)


def get_chart():
    return Chart.parse_file(get_chart_path())


if __name__ == "__main__":
    abacus()
