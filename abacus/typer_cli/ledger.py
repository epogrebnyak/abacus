from pathlib import Path

import typer
from typing_extensions import Annotated

from abacus.base import Amount
from abacus.typer_cli.base import get_entries_path

A = Annotated[list[str], typer.Option()]

ledger = typer.Typer(help="Post entries to ledger.", add_completion=False)

from typing import Optional

@ledger.command()
def init(file: Optional[Path]=None, overwrite: bool = False):
    """Load starting balances to ledger from JSON file."""
    entries_path = get_entries_path()
    if entries_path.exists() and not overwrite:
        print(f"Entries file ({entries_path}) already exists.")
        return 1
    else:
        Path(entries_path).touch()
        print(f"Created entries file: {entries_path}")
    if file:
        raise NotImplementedError
        print(f"Loading entries from {file}...")
    return 0

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
