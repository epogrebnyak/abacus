from json import dumps
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from abacus.typer_cli.base import get_ledger

A = Annotated[list[str], typer.Option()]

show = typer.Typer(help="Show chart and account information.", add_completion=False)


@show.command()
def account(name: str):
    """Show account information."""


@show.command()
def balances(
    json: bool = True,
    nonzero: bool = False,
    chart_file: Optional[Path] = None,
    store_file: Optional[Path] = None,
):
    """Show account balances."""
    ledger = get_ledger(chart_file, store_file)
    if nonzero:
        data = ledger.balances.nonzero().data
    else:
        data = ledger.balances.data
    print(dumps(data))
