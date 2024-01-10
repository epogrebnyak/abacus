import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path

from abacus.base import Amount

A = Annotated[list[str], typer.Option()]

ledger = typer.Typer(help="Post entries to ledger.", add_completion=False)


@ledger.command()
def start(path: Path):
    """Load starting balances to ledger from JSON file."""


@ledger.command()
def post(title: str, amount: Amount, debit: str, credit: str):
    """Post double entry."""


@ledger.command()
def post_compound(title: str, debits: list[str, Amount], credits: list[str, Amount]):
    """Post compound entry."""


@ledger.command()
def close():
    """Post closing entries."""
