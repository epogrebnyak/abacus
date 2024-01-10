"""

Ideas:
- Allow bx without arguments to show help.

"""
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from abacus.base import Amount
from abacus.core import BalanceSheet, IncomeStatement, TrialBalance
from abacus.entries_store import LineJSON
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


def cwd() -> Path:
    return Path(os.getcwd())


def get_chart_path() -> Path:
    return cwd() / "chart.json"


def get_entries_path() -> Path:
    return cwd() / "entries.linejson"


@dataclass
class Everything:
    chart_path: Path = field(default_factory=get_chart_path)
    entries_path: Path = field(default_factory=get_entries_path)

    @property
    def user_chart(self) -> UserChart:
        return UserChart.load(path=self.chart_path)

    @property
    def chart(self) -> UserChart:
        return self.user_chart.chart()

    @property
    def store(self) -> LineJSON:
        return LineJSON(path=self.entries_path)

    @property
    def ledger(self):
        return self.chart.ledger().post_many(entries=self.store.yield_entries())

    # TODO: use rename_dict for viewers
    def trial_balance(self):
        return TrialBalance.new(self.ledger)

    def balance_sheet(self):
        return BalanceSheet.new(self.ledger)

    def income_statement(self):
        ledger = self.chart.ledger()
        ledger.post_many(
            entries=self.store.yield_entries_for_income_statement(self.chart)
        )
        return IncomeStatement.new(ledger)

    def account_balances(self):
        return self.ledger.balances


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
