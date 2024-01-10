import typer
from typing_extensions import Annotated
from typing import Optional
from pathlib import Path

from abacus.base import Amount

A = Annotated[list[str], typer.Option()]

show = typer.Typer(help="Show chart and account information.", add_completion=False)


@show.command()
def chart(json: bool = False):
    """Show chart of accounts."""


@show.command()
def account(name: str, json: bool = False):
    """Show account information."""


@show.command()
def trial_balance(json: bool = False):
    """Show trial-balance."""


@show.command()
def balances(all: bool = False, json: bool = True):
    """Show account balances."""
