import sys
from typing import List, Optional

import typer
from typing_extensions import Annotated

from abacus.typer_cli.base import UserChartCLI, last

chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)


# FIXME: move company_name to project.py
@chart.command()
def init(company_name: Optional[str] = None, overwrite: bool = False):
    """Initialize chart file in current directory."""
    uci = UserChartCLI.default()
    if uci.path.exists() and not overwrite:
        print(f"Chart file ({uci.path}) already exists.")
        return 1
    else:
        # FIXME: move company_name to project.py
        uci.user_chart.company_name = company_name
        uci.save()
        print(f"  Created chart file: {uci.path}")
        return 0


def spaced(labels: list[str]) -> str:
    return " ".join(labels) + "."


@chart.command()
def add(
    labels: List[str],
    asset: Annotated[
        bool, typer.Option("--asset", "-a", help="Add assets accounts.")
    ] = False,
    capital: Annotated[
        bool, typer.Option("--capital", "-c", help="Add capital (equity) accounts.")
    ] = False,
    liability: Annotated[
        bool, typer.Option("--liability", "-l", help="Add liability accounts.")
    ] = False,
    income: Annotated[
        bool, typer.Option("--income", "-i", help="Add income accounts.")
    ] = False,
    expense: Annotated[
        bool, typer.Option("--expense", "-e", help="Add expense accounts.")
    ] = False,
    title: Annotated[
        Optional[str], typer.Option("--title", "-t", help="Set title for an account.")
    ] = None,
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
            sys.exit("Use only one or no flags.")


@chart.command()
def set(
    income_summary_account: Optional[str] = None,
    retained_earnings_account: Optional[str] = None,
    null_account: Optional[str] = None,
):
    """Set income summary, retained earnings or null accounts."""
    if not (income_summary_account or retained_earnings_account or null_account):
        sys.exit("No changes made.")
    uci = UserChartCLI.load()
    if income_summary_account:
        uci.user_chart.set_isa(income_summary_account)
        print(f"New income summary account is {income_summary_account}.")
    if retained_earnings_account:
        uci.user_chart.set_re(retained_earnings_account)
        print(f"New retained earnings account is {retained_earnings_account}.")
    if null_account:
        uci.user_chart.set_null(null_account)
        print(f"New null account is {null_account}.")
    uci.save()


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
    """Print chart."""
    print(UserChartCLI.load().user_chart.json(indent=4, ensure_ascii=False))


@chart.command()
def unlink(
    yes: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete project files?")
    ]
):
    """Permanently delete chart file in current directory."""
    if yes:
        try:
            UserChartCLI.default().path.unlink(missing_ok=False)
        except FileNotFoundError:
            sys.exit("No file to delete.")
    else:
        ...
