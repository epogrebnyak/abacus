import sys
from pathlib import Path

import click
import typer
from typing_extensions import Annotated
from typing import Optional

from abacus.base import Amount
from abacus.core import Entry
from abacus.typer_cli.base import get_entries_path, get_store, UserChartCLI, last

A = Annotated[list[str], typer.Option()]

ledger = typer.Typer(help="Post entries to ledger.", add_completion=False)


@ledger.command()
def init(overwrite: bool = False):
    """Initialize chart file in current directory."""
    entries_path = get_entries_path()
    if entries_path.exists() and not overwrite:
        print(f"Entries file ({entries_path}) already exists.")
        return 1
    else:
        Path(entries_path).touch()
        print(f"Created entries file: {entries_path}")
    return 0
    # FIXME: always exit with 0


@ledger.command()
def load(file: Path):
    """Load starting balances to ledger from JSON file."""
    raise NotImplementedError


@ledger.command()
def post(debit: str, credit: str, amount: Amount, title: Optional[str] = None):
    """Post double entry."""
    if not (entries_path := get_entries_path()).exists():
        sys.exit(
            f"Entries file not found: {entries_path}. Use `ledger init` command to create it"
        )
    if ":" in debit:
        uci = UserChartCLI.load()
        uci.user_chart.use(debit)
        uci.save()
        debit = last(debit)
    if ":" in credit:
        uci = UserChartCLI.load()
        uci.user_chart.use(credit)
        uci.save()
        credit = last(credit)
    get_store().append(Entry(debit, credit, amount))
    print(
        f"Posted to ledger: debit <{debit}> {amount}, credit <{credit}> {amount}. Title: {title}."
    )
    # FIXME: title is discarded


# Need a Click command here
# See how implemented in Click or https://github.com/tiangolo/typer/issues/387#issuecomment-1192866047
# @ledger.command()
# def post_compound(title: str, debits: list[tuple[str, Amount]], credits: list[tuple[str, Amount]]):
#    """Post compound entry."""


@ledger.callback()
def callback():
    """
    Typer app, including Click subapp
    """


@click.command()
def hello():
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo("Hello")


typer_click_object = typer.main.get_command(ledger)
typer_click_object.add_command(hello, "hello")

### TODO: Хотим добиться чтобы проходило `bx ledger hello`
###       Тут пример как сделать `bx hello`: https://typer.tiangolo.com/tutorial/using-click/
###       Вопрос как сделать `bx ledger hello`


@ledger.command()
def close():
    """Post closing entries."""
    raise NotImplementedError


@ledger.command()
def unlink(
    yes: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete project files?")
    ]
):
    """Permanently delete ledger file in current directory."""
    if yes:
        try:
            get_entries_path().unlink(missing_ok=False)
        except FileNotFoundError:
            sys.exit("No file to delete.")
    else:
        ...
