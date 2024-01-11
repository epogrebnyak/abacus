import sys
from typing import List, Optional

import typer
from typing_extensions import Annotated

from abacus.typer_cli.base import UserChartCLI

chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)


def spaced(labels: list[str]) -> str:
    return "Added to chart: " + " ".join(labels)


# TODO: создать тест test_chart.py и добавить реализацию задействованных команд (из cli.py)
# bx chart add -a cash ar paper
# bx chart add -c equity
# bx chart add --liability loan
# bx chart add income:sales expense:salaries,interest
# bx chart promote contra:equity:ts
# bx chart name ts "Treasury stock"
# bx chart offset sales refunds voids
# bx chart show --json


def last(label: str) -> str:
    return label.split(":")[-1]


@chart.command()
def add(
    labels: List[str],
    asset: Annotated[bool, typer.Option("--asset", "-a")] = False,
    capital: Annotated[bool, typer.Option("--capital", "-c")] = False,
    liability: Annotated[bool, typer.Option("--liability", "-l")] = False,
    income: Annotated[bool, typer.Option("--income", "-i")] = False,
    expense: Annotated[bool, typer.Option("--expense", "-e")] = False,
    title: Annotated[Optional[str], typer.Option("--title", "-t")] = None,
):
    """Add accounts to chart."""
    if len(labels) == 1 and title:
        name(last(labels[0]), title)
    match [asset, capital, liability, income, expense].count(True):
        case 0:
            print("Expecting labeles:", labels)
        case 1:
            print("Processing flag...")
        case _:
            sys.exit("Expecting only one flag or no flags.")


@chart.command()
def set(
    income_summary_account: Optional[str] = None,
    retained_earnings_account: Optional[str] = None,
    null_account: Optional[str] = None,
):
    """Set income summary, retained earnings or null account names."""
    if i := income_summary_account:
        print(f"New income summary account is {income_summary_account}.")
    if r := retained_earnings_account:
        print(f"New retained earnings account is {retained_earnings_account}.")
    if n := null_account:
        print(f"New null account is {null_account}.")
    if not (i or r or n):
        print("No changes made.")


@chart.command()
def name(name: str, title: str):
    """Set account title."""
    UserChartCLI.load().name(name, title).save()
    print(f"New title for {name} is {title}.")


@chart.command()
def offset(name: str, contra_names: list[str]):
    """Add contra accounts."""
    s = "" if len(contra_names) == 1 else "s"
    print(f"Added contra account{s} for {name}.", spaced(contra_names))


# TODO: may write test for this
@chart.command()
def show(json: bool = True):
    print(UserChartCLI.load().user_chart.json())
