import sys
from typing import List, Optional

import typer
from typing_extensions import Annotated

from abacus.typer_cli.base import UserChartCLI

chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)

# TODO: создать тест test_chart.py
# bx init
# bx chart add -a cash ar paper
# bx chart add -c equity
# bx chart add --liability loan
# bx chart add income:sales expense:salaries,interest
# bx chart add contra:equity:ts --title "Treasury stock"
# bx chart name paper "Inventory (paper products)"
# bx chart offset sales refunds voids
# bx chart show --json
# bx unlink --yes


@chart.command()
def init(company_name: Optional[str] = None, overwrite: bool = False):
    """Initialize chart file in current directory."""
    uci = UserChartCLI.default()
    if uci.path.exists() and not overwrite:
        print(f"Chart file ({uci.path}) already exists.")
        return 1
    else:
        uci.user_chart.company_name = company_name
        uci.save()
        print(f"  Created chart file: {uci.path}")
        return 0


def spaced(labels: list[str]) -> str:
    return " ".join(labels) + "."


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
    uci = UserChartCLI.load()
    match [asset, capital, liability, income, expense].count(True):
        case 0:
            uci.user_chart.use(*labels)
            uci.save()
            print("Added accounts:", spaced(labels))
        case 1:
            if asset:
                prefix = "asset"
            if capital:
                prefix = "capital"
            if liability:
                prefix = "liability"
            if income:
                prefix = "income"
            if expense:
                prefix = "expense"
            uci.user_chart.use(*labels, prefix=prefix)
            uci.save()
            print(f"Added accounts ({prefix}):", spaced(labels))
        case _:
            sys.exit("Expecting only one or no flags.")


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
def name(account_name: str, title: str):
    """Set account title."""
    uci = UserChartCLI.load()
    uci.user_chart.name(account_name, title)
    uci.save()
    print(f"New title for {account_name} is {title}.")


@chart.command()
def offset(name: str, contra_names: list[str]):
    """Add contra accounts."""
    uci = UserChartCLI.load()
    for contra_name in contra_names:
        uci.user_chart.offset(name, contra_name)
    uci.save()
    s = "" if len(contra_names) == 1 else "s"
    print(f"Added contra account{s} for {name}:", spaced(contra_names))


@chart.command()
def show(json: bool = True):
    print(UserChartCLI.load().user_chart.json(indent=4, ensure_ascii=False))
