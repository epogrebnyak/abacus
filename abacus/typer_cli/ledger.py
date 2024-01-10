from pathlib import Path

import typer
from typing_extensions import Annotated

from abacus.base import Amount

A = Annotated[list[str], typer.Option()]

ledger = typer.Typer(help="Post entries to ledger.", add_completion=False)


@ledger.command()
def load(path: Path):
    """Load starting balances to ledger from JSON file."""


@ledger.command()
def post(title: str, amount: Amount, debit: str, credit: str):
    """Post double entry."""


# TODO: may need a Click command here
#       See how implemented in Click or https://github.com/tiangolo/typer/issues/387#issuecomment-1192866047
#

# @ledger.command()
# def post_compound(title: str, debits: list[tuple[str, Amount]], credits: list[tuple[str, Amount]]):
#     """Post compound entry."""


@ledger.command()
def close():
    """Post closing entries."""
