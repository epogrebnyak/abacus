import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import click

from abacus import AbacusError, Chart
from abacus.cli.chart_command import ChartCommand
from abacus.cli.ledger_command import LedgerCommand


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


def chart_command(path: Path | None = None) -> ChartCommand:
    """Chart command based on local chart.json file."""
    if path is None:
        path = get_chart_path()
    return ChartCommand(chart=Chart.parse_file(path), path=path)


def get_chart() -> Chart:
    return chart_command().chart


def ledger_command() -> LedgerCommand:
    return LedgerCommand(path=get_entries_path())


@click.group()
def abacus():
    pass


@abacus.group()
def chart():
    """Define chart of accounts."""


@chart.command(name="init")
def init_chart():
    """Create chart of accounts file (chart.json) in current folder."""
    handler = ChartCommand(path=get_chart_path(), chart=Chart())
    handler.assert_does_not_exist().write().echo()


def promote(account_name: str):
    """Safe add account to chart."""
    try:
        chart_command().promote(account_name).echo().write()
    except AbacusError as e:
        sys.exit(str(e))


def last(account_identifier: str) -> str:
    """Get last item of account identifier."""
    return account_identifier.split(":")[-1]


def name(account_name, title) -> None:
    chart_command().set_name(last(account_name), title).echo().write()


@chart.command
@click.argument("account_name", type=str)
@click.option("--title", type=str, required=False, help="Account title.")
def add(account_name: str, title: str):
    """Add account to chart.

    Examples:
        abacus chart add asset:cash --title "Cash and equivalents"
        abacus chart add expense:rent
        abacus chart add asset:ppe --title "Property, plant and equipment"
        abacus chart add contra:ppe:depreciation --title "Accumulated depreciation"
    """
    promote(account_name)
    if title:
        name(account_name, title)


@chart.command
@click.argument("prefix")
@click.argument("account_names", nargs=-1)
def add_many(prefix, account_names: List[str]):
    """Add several accounts to chart.

    Example:
        abacus chart add-many asset cash inventory ar ppe
        abacus chart add-many contra:sales refunds voids
    """
    for account_name in account_names:
        promote(prefix + ":" + account_name)


@chart.command(name="name")
@click.argument("account_name")
@click.option("--title", type=str, required=False, help="Account title.")
def name_command(account_name, title):
    """Change account title."""
    name(account_name, title)


@chart.command
@click.argument("name")
@click.option("--debit", required=True, type=str, help="Debit account.")
@click.option("--credit", required=True, type=str, help="Credit account.")
# FIXME: make required option
# @click.option("--requires")
def operation(name, debit, credit):
    """Define a named pair of debit and credit accounts."""
    chart_command().add_operation(name, debit, credit).echo().write()


@chart.command(name="set")
@click.option(
    "--retained-earnings-account",
    "re",
    type=str,
    required=False,
    help="Retained earnings account name.",
)
@click.option(
    "--null-account", "null", type=str, required=False, help="Null account name."
)
@click.option(
    "--income-summary-account",
    "isa",
    type=str,
    required=False,
    help="Income summary account name.",
)
def set_special_accounts(re, null, isa):
    """Change default names of retained earnings, income summary or null account."""
    command = chart_command()
    if re:
        command.set_retained_earnings(re)
    if null:
        command.set_null_account(null)
    if isa:
        command.set_isa(isa)
    command.echo().write()


@chart.command(name="show")
@click.option("--json", "json_flag", is_flag=True, help="Show chart as JSON.")
def show_chart(json_flag):
    """Print chart of accounts."""
    command = chart_command()
    if json_flag:
        click.echo(command.json())
    else:
        click.echo(command.show())


@chart.command(name="unlink")
@click.confirmation_option(
    prompt=f"Are you sure you want to permanently delete {get_chart_path()}?"
)
def unlink_chart():
    """Permanently delete chart of accounts file in current folder."""
    ChartCommand(path=get_chart_path()).unlink()


@abacus.group()
def ledger():
    """Post entries to ledger."""


@ledger.command(name="init")
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="JSON file with account starting balances.",
)
def init_ledger(file):
    """Create ledger file (entries.linejson) in current folder."""
    handler = LedgerCommand(path=get_entries_path()).init().echo()
    if file:
        starting_balances = read_starting_balances(file)
        handler.post_starting_balances(get_chart(), starting_balances).echo()


def read_starting_balances(path: str) -> Dict:
    """Read starting balances from JSON file at *path*."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


@ledger.command
@click.option("--debit", required=True, type=str, help="Debit account name.")
@click.option("--credit", required=True, type=str, help="Credit account name.")
@click.option("--amount", required=True, type=int, help="Transaction amount.")
def post(debit, credit, amount):
    """Post double entry to ledger."""
    chart_command().promote(debit).promote(credit).echo().write()
    ledger_command().post_entry(last(debit), last(credit), amount).echo()


@ledger.command(name="post-compound")
@click.option("--debit", type=(str, int), multiple=True)
@click.option("--credit", type=(str, int), multiple=True)
def post_compound(debit, credit):
    """Post compound entry to ledger."""
    chart_handler = chart_command()
    for account, _ in debit + credit:
        chart_handler.promote(account)
    chart_handler.echo().write()

    def apply_last(tuples):
        return [(last(account), amount) for account, amount in tuples]

    ledger_handler = ledger_command()
    ledger_handler.post_compound(
        get_chart(), apply_last(debit), apply_last(credit)
    ).echo()


@click.option("--operation", "-o", "operations", type=(str, int), multiple=True)
@ledger.command
def post_operation(operations):
    """Post named operation(s) to ledger."""
    ledger_command().post_operations(get_chart(), operations).echo()


@ledger.command
def close():
    """Close ledger at accounting period end."""
    # FIXME: allows to close accidentally twice
    ledger_command().post_closing_entries(chart=get_chart()).echo()


@ledger.command(name="show")
def show_ledger():
    """Print ledger."""
    ledger_command().show()


@ledger.command(name="unlink")
@click.confirmation_option(
    prompt=f"Are you sure you want to permanently delete {get_entries_path()}?"
)
def unlink_ledger():
    """Permanently delete ledger file in current folder."""
    ledger_command().unlink()


@abacus.group
def report():
    """Show reports."""


@report.command(name="trial-balance")
def trial_balance():
    """Show trial balance."""
    from abacus.cli.report_command import trial_balance

    click.echo(trial_balance(get_entries_path(), get_chart_path()))


def verify_flag(plain: bool, json_flag: bool, rich: bool):
    match sum(1 for x in [plain, json_flag, rich] if x):
        case 0:
            return True  # default is --plain
        case 1:
            return plain  # keep as is
        case _:
            sys.exit("Choose one of --plain, --json or --rich.")


def echo_statement(statement, chart_, plain, json_flag, rich):
    plain = verify_flag(plain, json_flag, rich)
    if json_flag:
        click.echo(statement.json())
    elif rich:
        click.echo(statement.print_rich(chart_.names))
    elif plain:
        click.echo(statement.view(chart_.names))


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
    echo_statement(statement, get_chart(), plain, json, rich)


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
    echo_statement(statement, get_chart(), plain, json, rich)


@report.command(name="balances")
@click.option("--nonzero", is_flag=True, help="Omit accounts with zero balances.")
def balances(nonzero):
    """Show account balances."""
    from abacus.cli.report_command import account_balances

    balances = account_balances(
        entries_path=get_entries_path(), chart_path=get_chart_path(), nonzero=nonzero
    )
    click.echo(jsonify(balances))


def jsonify(x):
    return json.dumps(x, indent=4, sort_keys=True, ensure_ascii=False)


@report.command()
@click.argument("account_name")
@click.option("--assert-balance", type=int, help="Verify account balance.")
def account(account_name: str, assert_balance: int):
    """Show or check account information."""
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


if __name__ == "__main__":
    abacus()
