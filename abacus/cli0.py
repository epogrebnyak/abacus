import json
import os
import sys
from pathlib import Path

import click  # type: ignore

from abacus.core import (
    AbacusError,
    BalanceSheet,
    Chart,
    CompoundEntry,
    Entry,
    IncomeStatement,
    Pipeline,
    TrialBalance,
)
from abacus.entries_store import LineJSON
from abacus.user_chart import UserChart


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
    return ledger.balances.data


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
        UserChart.default_user_chart().set_path(chart_path).save()
        print(f"Created chart file: {chart_path}")
    entries_path = get_entries_path()
    if entries_path.exists():
        print(f"Entries file ({entries_path}) already exists.")
        exit_code = 1
    else:
        Path(entries_path).touch()
        print(f"Created entries file: {entries_path}")
    sys.exit(exit_code)


@cx.command(name="add")
@click.argument("account_names", required=True, type=str, nargs=-1)
@click.option("--title", required=False, type=str, help="Account title")
def cx_add(account_names, title):
    """Add account to chart."""
    try:
        user_chart = get_user_chart().use(*account_names)
        print(f"Added to chart: {' '.join(account_names)}.")
        if len(account_names) == 1 and title:
            user_chart.name(account_names[0], title)
            print("Account title:", title)
        user_chart.save()
    except (AbacusError, FileNotFoundError) as e:
        sys.exit(str(e))


@cx.command(name="name")
@click.argument("account_name")
@click.argument("title")
def name(account_name, title):
    get_user_chart().name(last(account_name), title).save()
    print("Account title:", title)


@cx.command(name="post")
@click.argument("debit", required=True, type=str)
@click.argument("credit", required=True, type=str)
@click.argument("amount", required=True, type=int)
@click.option("--title", required=False, type=str, help="Entry title.")
def cx_post(debit, credit, amount, title):
    """Post double entry to ledger."""
    if not (entries_path := get_entries_path()).exists():
        sys.exit(f"FileNotFoundError: {entries_path}")
    # FIXME: title is discarded
    if ":" in debit:
        UserChart.load().use(debit).save()
        debit = last(debit)
    if ":" in credit:
        UserChart.load().use(credit).save()
        credit = last(credit)
    get_store().append(Entry(debit, credit, amount))
    print(f"Posted to ledger: debit <{debit}> {amount}, credit <{credit}> {amount}.")


def last(s):
    return s.split(":")[-1]


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
@click.option(
    "--all",
    "all_reports_flag",
    is_flag=True,
    help="Show all reports.",
)
def cx_report(
    trial_balance_flag,
    balance_sheet_flag,
    income_statement_flag,
    account_balances_flag,
    all_reports_flag,
):
    """Show reports."""
    from abacus.viewers import print_viewers

    rename_dict = get_user_chart().rename_dict
    if trial_balance_flag and not all_reports_flag:
        trial_balance().viewer.print()
    if balance_sheet_flag and not all_reports_flag:
        balance_sheet().viewer.use(rename_dict).print()
    if income_statement_flag and not all_reports_flag:
        income_statement().viewer.use(rename_dict).print()
    if account_balances_flag:
        print(json.dumps(account_balances()))
    if all_reports_flag:
        tv = trial_balance().viewer
        bv = balance_sheet().viewer.use(rename_dict)
        iv = income_statement().viewer.use(rename_dict)
        print_viewers({}, tv, bv, iv)


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
    user_chart = get_user_chart()
    if isa:
        user_chart.set_isa(isa)
    if re:
        user_chart.set_re(re)
    if null:
        user_chart.set_null(null)
    user_chart.save(path=get_chart_path())


@cx.command(name="load")
@click.argument("file", type=click.Path(exists=True))
def load(file):
    """Load starting balances from JSON file."""
    from abacus.core import AccountBalances, starting_entries

    balances = AccountBalances.load(file)
    chart = get_chart()
    entries = starting_entries(chart, balances)
    get_store().append_many(entries)
    print("Loaded starting balances from", file)


@cx.command(name="post-compound")
@click.option("--debit", type=(str, int), multiple=True)
@click.option("--credit", type=(str, int), multiple=True)
def post_compound(debit, credit):
    """Post compound entry."""
    chart = get_chart()
    store = get_store()
    entries = CompoundEntry(debits=debit, credits=credit).to_entries(chart.null_account)
    store.append_many(entries)


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


@cx.command("assert")
@click.argument("account_name")
@click.argument("balance", type=int)
def assert_balance(account_name, balance):
    """Verify account balance."""
    ab = account_balances()
    fact = ab[account_name]
    if fact != balance:
        sys.exit(f"{account_name} balance is {fact}, expected {balance}.")


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
