import os
import sys
from pathlib import Path

import typer
from typing_extensions import Annotated

from abacus.base import Amount
from abacus.core import BalanceSheet, Chart, IncomeStatement, TrialBalance
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
    return ledger.balances


app = typer.Typer(
    add_completion=False, help="A minimal yet valid double entry accounting system."
)
chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)
add = typer.Typer(help="Add accounts to chart.", add_completion=False)
app.add_typer(chart, name="chart")
chart.add_typer(add, name="add")


@app.command()
def about():
    """Show information about `abacus` package."""
    print("abacus")


@app.command()
def init(company_name: str):
    """Initialize project files in current directory."""
    exit_code = 0
    chart_path = get_chart_path()
    if chart_path.exists():
        print(f"Chart file ({chart_path}) already exists.")
        exit_code = 1
    else:
        UserChart.default_user_chart(company_name).save(chart_path)
        print(f"Created chart file: {chart_path}")
    entries_path = get_entries_path()
    if entries_path.exists():
        print(f"Entries file ({entries_path}) already exists.")
        exit_code = 1
    else:
        Path(entries_path).touch()
        print(f"Created entries file: {entries_path}")
    sys.exit(exit_code)


@add.command()
def assets(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def capital(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def liabilities(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def income(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def expenses(names: list[str]):
    print(f"Accepted names: {names}")


@add.command()
def labels(labels: list[str]):
    print(f"Accepted names: {labels}")


# @chart.command()
# def set_retained_earnings(name: str):
#     """Set retained earnings account."""
#     print(f"Accepted name: {name}")


@chart.command()
def name(name: str, title: str):
    """Set account title."""
    print(f"Renaming {name} to {title}.")


@chart.command()
def offset(name: str, contra_names: list[str]):
    """Add contra accounts."""
    print(f"Offsetting {name} with {contra_names}.")


@app.command()
def load(path: str):
    """Load starting balances from JSON file."""


@app.command()
def post(title: str, amount: Amount, debit: str, credit: str):
    """Post double entry."""


@app.command()
def post_compound(title: str, debits: list[str, Amount], credits: list[str, Amount]):
    """Post compound entry."""


@app.command()
def close():
    """Post closing entries."""


@app.command()
def report(
    trial_balance: bool = False,
    balance_sheet: bool = False,
    income_statement: bool = False,
    account_balances: bool = False,
    all: bool = False,
):
    """Show reports."""


@app.command(name="assert")
def assert_(name, balance: Amount):
    """Verify account balance."""


@app.command()
def unlink(
    yes: Annotated[bool, typer.Option(prompt="Are you sure you want to delete project files?")]
):
    """Permanently delete project files in current directory."""
    if yes:
        get_chart_path().unlink(missing_ok=True)
        get_entries_path().unlink(missing_ok=True)

    else:
        ...


if __name__ == "__main__":
    app()
