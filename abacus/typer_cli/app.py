import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from abacus.typer_cli.base import get_chart_path, get_entries_path, get_ledger
from abacus.typer_cli.chart import chart
from abacus.typer_cli.ledger import ledger
from abacus.typer_cli.show import show

from .post import postx

app = typer.Typer(
    add_completion=False, help="A minimal yet valid double entry accounting system."
)
app.add_typer(chart, name="chart")
app.add_typer(ledger, name="ledger")
app.add_typer(show, name="show")


@app.callback()
def callback():
    """
    Typer app, including Click subapp
    """


@app.command()
def init():
    from abacus.typer_cli.chart import init as chart_init
    from abacus.typer_cli.ledger import init as ledger_init

    chart_init()
    ledger_init()


@app.command()
def report(
    balance_sheet: Annotated[
        bool,
        typer.Option("--balance-sheet", "-b", help="Show balance sheet."),
    ] = False,
    income_statement: Annotated[
        bool,
        typer.Option("--income-statement", "-i", help="Show income statement."),
    ] = False,
    trial_balance: Annotated[
        bool,
        typer.Option("--trial-balance", "-t", help="Show trial balance."),
    ] = False,
    all: Annotated[bool, typer.Option("--all", help="Show all statements.")] = False,
):
    """Show reports."""


@app.command(name="assert")
def assert_(
    name: str,
    balance: int,
    chart_file: Optional[Path] = None,
    ledger_file: Optional[Path] = None,
):
    """Verify account balance."""
    ledger = get_ledger(chart_file, ledger_file)
    if not (fact := ledger.balances[name]) == balance:
        sys.exit(f"Account {name} balance is {fact}, expected {balance}.")


@app.command()
def unlink(
    yes: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete project files?")
    ]
):
    """Permanently delete project files in current directory."""
    if yes:
        get_chart_path().unlink(missing_ok=True)
        get_entries_path().unlink(missing_ok=True)

    else:
        ...


combined_typer_click_app = typer.main.get_command(app)
combined_typer_click_app.add_command(postx, "post")  # type: ignore
