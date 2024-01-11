import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from abacus.core import Amount
from abacus.typer_cli.base import get_chart_path, get_entries_path
from abacus.typer_cli.chart import chart
from abacus.typer_cli.ledger import ledger
from abacus.typer_cli.show import show
from abacus.user_chart import UserChart

app = typer.Typer(
    add_completion=False, help="A minimal yet valid double entry accounting system."
)
app.add_typer(chart, name="chart")
app.add_typer(ledger, name="ledger")
app.add_typer(show, name="show")


@app.command()
def about():
    """Show information about `abacus` package."""
    print("abacus")


@app.command()
def init(company_name: Optional[str] = None, overwrite: bool = False):
    """Initialize project files in current directory."""
    exit_code = 0
    chart_path = get_chart_path()
    if chart_path.exists() and not overwrite:
        print(f"Chart file ({chart_path}) already exists.")
        exit_code = 1
    else:
        UserChart.default_user_chart(company_name).save(chart_path)
        print(f"Created chart file: {chart_path}")
    entries_path = get_entries_path()
    if entries_path.exists() and not overwrite:
        print(f"Entries file ({entries_path}) already exists.")
        exit_code = 1
    else:
        Path(entries_path).touch()
        print(f"Created entries file: {entries_path}")
    sys.exit(exit_code)


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
def assert_(name: str, balance: Amount):
    """Verify account balance."""


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
