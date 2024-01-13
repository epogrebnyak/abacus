import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from abacus.base import AbacusError, Amount
from abacus.core import AccountBalances, Entry, starting_entries
from abacus.entries_store import LineJSON
from abacus.typer_cli.base import last
from abacus.user_chart import UserChart

A = Annotated[list[str], typer.Option()]
ledger = typer.Typer(help="Modify ledger.", add_completion=False)


def assure_ledger_file_exists(store_file):
    path = LineJSON.load(store_file).path
    if not path.exists():
        sys.exit(
            f"Ledger file ({path}) not found. Use `ledger init` command to create it."
        )


@ledger.command()
def init():
    """Initialize ledger file in current directory."""
    store_path = LineJSON.load(None).path
    if store_path.exists():
        print(f"Ledger file ({store_path}) already exists.")
    else:
        store_path.touch()
        print(f"Created empty ledger file ({store_path}).")


@ledger.command()
def load(
    file: Path, chart_file: Optional[Path] = None, store_file: Optional[Path] = None
):
    """Load starting balances to ledger from JSON file."""
    store = LineJSON.load(store_file)
    # FIXME: store must be empty for load() command
    balances = AccountBalances.load(file)
    chart = UserChart.load(chart_file).chart()
    entries = starting_entries(chart, balances)
    store.append_many(entries)
    print("Posted starting balances to ledger:", entries)


@ledger.command()
def post(
    debit: str,
    credit: str,
    amount: Amount,
    title: Optional[str] = None,
    chart_file: Optional[Path] = None,
    store_file: Optional[Path] = None,
):
    """Post double entry."""
    assure_ledger_file_exists(store_file)
    if ":" in debit:
        try:
            UserChart.load(chart_file).use(debit).save()
        except AbacusError:
            pass
        debit = last(debit)
    if ":" in credit:
        try:
            UserChart.load(chart_file).use(credit).save()
        except AbacusError:
            pass
        credit = last(credit)
    LineJSON.load(store_file).append(Entry(debit, credit, amount))
    print(f"Debited {debit} {amount} and credited {credit} {amount}.")
    # FIXME: title is discarded
    print("Title:", title)


@ledger.command()
def show(store_file: Optional[Path] = None):
    """Show ledger."""
    assure_ledger_file_exists(store_file)
    print(LineJSON.load(store_file).path.read_text())


@ledger.command()
def unlink(
    yes: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete ledger file?")
    ]
):
    """Permanently delete ledger file in current directory."""
    if yes:
        LineJSON.load().path.unlink(missing_ok=True)
