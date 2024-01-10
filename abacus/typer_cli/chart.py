from typing import Optional, List

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


# TODO: создать тест test_chart.py и добавить реализацию задейтсвованных команд (из cli.py)         
# bx chart add --asset cash -c equity -l loan
# bx chart promote income:sales expense:salaries,interest 
# bx chart promote contra:equity:ts
# bx chart name ts "Treasury stock"
# bx chart offset sales refunds voids
# bx show chart --json        

@chart.command()
def add(
    asset: Annotated[List[str], typer.Option("--asset", "-a")] = [],
    capital: Annotated[List[str], typer.Option("--capital", "-c")] = [],
    liability: Annotated[List[str], typer.Option("--liability", "-l")] = [],
    income: Annotated[List[str], typer.Option("--income", "-i")] = [],
    expense: Annotated[List[str], typer.Option("--expense", "-e")] = [],
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
