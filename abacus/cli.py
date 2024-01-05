import json
import os
import sys
from pathlib import Path

import click

from abacus.core import (
    AbacusError,
    BalanceSheet,
    Chart,
    Entry,
    IncomeStatement,
    Pipeline,
    TrialBalance,
)
from abacus.entries_store import LineJSON
from abacus.show import show
from abacus.user_chart import UserChart, user_chart


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


def get_user_chart() -> UserChart:
    return UserChart.load(path=get_chart_path())


def get_chart() -> Chart:
    return get_user_chart().chart()


def get_store() -> LineJSON:
    return LineJSON(path=get_entries_path())


def get_current_ledger():
    chart = get_chart()
    store = get_store()
    ledger = chart.ledger()
    ledger.post_many(entries=store.yield_entries())
    return ledger


def trial_balance():
    ledger = get_current_ledger()
    return TrialBalance.new(ledger)


def balance_sheet():
    ledger = get_current_ledger()
    return BalanceSheet.new(ledger)


def income_statement():
    chart = get_chart()
    store = get_store()
    ledger = chart.ledger()
    ledger.post_many(entries=store.yield_entries_for_income_statement(chart))
    return IncomeStatement.new(ledger)


def account_balances():
    ledger = get_current_ledger()
    return ledger.balances


@click.group()
def cx():
    """Minimal tool for complete accounting cycle."""


@cx.command(name="init")
def cx_command():
    """Initialize chart and ledger files."""
    exit_code = 0
    chart_path = get_chart_path()
    if chart_path.exists():
        print(f"Chart file ({chart_path}) already exists.")
        exit_code = 1
    else:
        user_chart().save(chart_path)
    entries_path = get_entries_path()
    if entries_path.exists():
        print(f"Entries file ({entries_path}) already exists.")
        exit_code = 1
    else:
        Path(entries_path).touch()
    sys.exit(exit_code)


@cx.command(name="add")
@click.argument("account_names", required=True, type=str, nargs=-1)
def cx_add(account_names):
    """Add account to chart."""
    try:
        get_user_chart().use(*account_names).save(path=get_chart_path())
        print(f"Added to chart: {' '.join(account_names)}.")
    except (AbacusError, FileNotFoundError) as e:
        sys.exit(str(e))


@cx.command(name="name")
@click.argument("account_name", type=str)
@click.argument("title", type=str)
def cx_name(account_name, title):
    """Set account title."""
    name(account_name, title)


# TODO
def name(account_name, title) -> None:
    print(" Name:", account_name)
    print("Title:", title)


@cx.command(name="post")
@click.option("--debit", required=True, type=str, help="Debit account name.")
@click.option("--credit", required=True, type=str, help="Credit account name.")
@click.option("--amount", required=True, type=int, help="Transaction amount.")
def cx_post(debit, credit, amount):
    """Post double entry to ledger."""
    if not (entries_path := get_entries_path()).exists():
        sys.exit(f"FileNotFoundError: {entries_path()}")
    get_store().append(Entry(debit, credit, amount))
    print(f"Posted to ledger: debit <{debit}> {amount}, credit <{credit}> {amount}.")


@cx.command(name="close")
def cx_close():
    """Closing accounts at period end."""
    chart = get_chart()
    ledger = get_current_ledger()
    p = Pipeline(chart, ledger).close()
    get_store().append_many(p.closing_entries)


@cx.command(name="report")
@click.option(
    "--trial-balance",
    "-t",
    "trial_balance_flag",
    is_flag=True,
    help="Show trial balance.",
)
@click.option(
    "--balance-sheet",
    "-b",
    "balance_sheet_flag",
    is_flag=True,
    help="Show balance sheet.",
)
@click.option(
    "--income-statement",
    "-i",
    "income_statement_flag",
    is_flag=True,
    help="Show income statement.",
)
@click.option(
    "--account-balances",
    "-a",
    "account_balances_flag",
    is_flag=True,
    help="Show account balances.",
)
def cx_report(
    trial_balance_flag, balance_sheet_flag, income_statement_flag, account_balances_flag
):
    """Show reports."""
    if trial_balance_flag:
        print(show(trial_balance()))
    if balance_sheet_flag:
        print(show(balance_sheet()))
    if income_statement_flag:
        print(show(income_statement()))
    if account_balances_flag:
        print(account_balances())


# cx init
# cx add asset:cash
# cx add capital:equity contra:equity:ts
# cx name ts --title "Treasury shares"
# cx add asset:cash --title "Cash and equivalents"
# assume the rest have no :
# cx add --prefix=asset goods ar
# cx name ar --title "Accounts receivable"
# cx offset equity ts --title "Treasury shares"
# cx add income:sales
# cx offset sales voids refunds cashback
# cx alias --operation capitalize --debit cash --credit equity
# cx set --income-summary-account current_profit
# cx set --retained-earings-account re
# cx set --null-account null

# def add_many(account_labels, prefix):
#     """Add several accounts to chart.

#     \b
#     Example:
#       abacus chart add-many asset:cash capital:equity
#       abacus chart add-many --prefix=asset ar goods
#     """
#     click.echo(account_labels, prefix)


@cx.group(name="extra")
def extra():
    """More commands."""


@extra.command(name="unlink")
@click.confirmation_option(
    prompt="Are you sure you want to permanently delete project files?"
)
def cx_unlink():
    """Permanently delete chart and ledger files."""
    get_chart_path().unlink(missing_ok=True)
    get_entries_path().unlink(missing_ok=True)


@extra.command(name="set")
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
    """Change default account names (isa, re, null)."""
    # command = chart_command()
    # if re:
    #     command.set_retained_earnings(re)
    # if null:
    #     command.set_null_account(null)
    # if isa:
    #     command.set_isa(isa)
    # command.echo().write()


@extra.command(name="load")
@click.argument("file", type=click.Path(exists=True))
def init_ledger(file):
    """Load starting balances from JSON file."""
    # handler = LedgerCommand(path=get_entries_path()).init().echo()
    # if file:
    #     starting_balances = read_starting_balances(file)
    #     handler.post_starting_balances(get_chart(), starting_balances).echo()


# @ledger.command
# @click.option("--debit", required=True, type=str, help="Debit account name.")
# @click.option("--credit", required=True, type=str, help="Credit account name.")
# @click.option("--amount", required=True, type=int, help="Transaction amount.")
# @click.option("--title")
# def post(debit, credit, amount, title):
#     """Post double entry to ledger."""
#     chart_command().promote(debit).promote(credit).echo().write()
#     ledger_command().post_entry(last(debit), last(credit), amount).echo()
#     # FIXME: title not used


# @ledger.command(name="post-compound")
# @click.option("--debit", type=(str, int), multiple=True)
# @click.option("--credit", type=(str, int), multiple=True)
# def post_compound(debit, credit):
#     """Post compound entry to ledger."""
#     chart_handler = chart_command()
#     for account, _ in debit + credit:
#         chart_handler.promote(account)
#     chart_handler.echo().write()

#     def apply_last(tuples):
#         return [(last(account), amount) for account, amount in tuples]

#     ledger_handler = ledger_command()
#     ledger_handler.post_compound(
#         get_chart(), apply_last(debit), apply_last(credit)
#     ).echo()


# @ledger.command
# def close():
#     """Close ledger at accounting period end."""
#     # FIXME: allows to close accidentally twice
#     ledger_command().post_closing_entries(chart=get_chart()).echo()


# @ledger.command(name="show")
# def show_ledger():
#     """Print ledger."""
#     ledger_command().show()


# @abacus.group
# def report():
#     """Show reports."""


# @report.command()
# def trial_balance():
#     """Show trial balance."""
#     from abacus.cli.report_command import trial_balance

#     click.echo(trial_balance(get_entries_path(), get_chart_path()))


# def verify_flag(plain: bool, json_flag: bool, rich: bool):
#     match sum(1 for x in [plain, json_flag, rich] if x):
#         case 0:
#             return True  # default is --plain
#         case 1:
#             return plain  # keep as is
#         case _:
#             sys.exit("Choose one of --plain, --json or --rich.")


# def echo_statement(statement, chart_, plain, json_flag, rich):
#     plain = verify_flag(plain, json_flag, rich)
#     if json_flag:
#         click.echo(statement.json())
#     elif rich:
#         click.echo(statement.print_rich(chart_.titles))
#     elif plain:
#         click.echo(statement.view(chart_.titles))


# @report.command(name="balance-sheet")
# @click.option(
#     "--plain",
#     is_flag=True,
#     help="Plain text output [default].",
# )
# @click.option(
#     "--rich",
#     is_flag=True,
#     help="Rich text output.",
# )
# @click.option("--json", is_flag=True, help="Format output as JSON.")
# def balance_sheet(plain, rich, json):
#     """Show balance sheet."""
#     from abacus.cli.report_command import balance_sheet

#     statement = balance_sheet(get_entries_path(), get_chart_path())
#     echo_statement(statement, get_chart(), plain, json, rich)


# @report.command(name="income-statement")
# @click.option(
#     "--plain",
#     is_flag=True,
#     help="Plain text output [default].",
# )
# @click.option(
#     "--rich",
#     is_flag=True,
#     help="Rich text output.",
# )
# @click.option("--json", is_flag=True, help="Format output as JSON.")
# def income_statement(plain, rich, json):
#     """Show income statement."""
#     from abacus.cli.report_command import income_statement

#     statement = income_statement(get_entries_path(), get_chart_path())
#     echo_statement(statement, get_chart(), plain, json, rich)


# @abacus.group(name="account")
# def accounts():
#     """Show account information."""


# @accounts.command()
# @click.argument("account_name")
# def show(account_name: str):
#     """Show detailed account information."""
#     from abacus.cli.inspect_command import print_account_info
#     from abacus.cli.report_command import current_ledger

#     ledger = current_ledger(
#         chart_path=get_chart_path(), entries_path=get_entries_path()
#     )
#     print_account_info(ledger, get_chart(), account_name)


# @accounts.command("assert")
# @click.option("--balance", type=(str, int), multiple=True)
# def assert_balance(balance):
#     """Verify account balance."""
#     from abacus.cli.inspect_command import assert_account_balance
#     from abacus.cli.report_command import current_ledger

#     ledger = current_ledger(
#         chart_path=get_chart_path(), entries_path=get_entries_path()
#     )
#     for account_name, balance_ in balance:
#         assert_account_balance(ledger, account_name, balance_)


# @accounts.command(name="show-balances")
# @click.option("--nonzero", is_flag=True, help="Omit accounts with zero balances.")
# def json_balances(nonzero):
#     """Show account balances as JSON."""
#     from abacus.cli.report_command import account_balances

#     balances = account_balances(
#         entries_path=get_entries_path(), chart_path=get_chart_path(), nonzero=nonzero
#     )
#     click.echo(jsonify(balances))


def jsonify(x):
    return json.dumps(x, indent=4, sort_keys=True, ensure_ascii=False)


# @accounts.command(name="list")
# def list_accounts():
#     """List available accounts."""


if __name__ == "__main__":
    cx()
