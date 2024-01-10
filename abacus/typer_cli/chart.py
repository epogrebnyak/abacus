from typing import Optional

import typer
from typing_extensions import Annotated

A = Annotated[list[str], typer.Option()]

chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)


def spaced(labels: list[str]) -> str:
    return "Added to chart: " + " ".join(labels)


# TODO/TEST:
# bx chart promote asset:cash capital:equity contra:equity:ts
@chart.command()
def promote(labels: list[str]):
    """Add accounts to chart by label (like 'asset:cash')."""
    if labels:
        print(spaced(labels))


# TODO/TEST:
# bx chart add --asset cash --capital equity
@chart.command()
def add(
    asset: A = [],
    liability: A = [],
    capital: A = [],
    income: A = [],
    expense: A = [],
):
    """Add accounts to chart."""
    if asset:
        print(spaced(asset))
    if capital:
        print(spaced(capital))
    if liability:
        print(spaced(liability))
    if income:
        print(spaced(income))
    if expense:
        print(spaced(expense))


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
    print(f"New title for {name} is {title}.")


@chart.command()
def offset(name: str, contra_names: list[str]):
    """Add contra accounts."""
    s = "" if len(contra_names) == 1 else "s"
    print(f"Added contra account{s} for {name}.", spaced(contra_names))
