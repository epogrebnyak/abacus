import sys
from pathlib import Path
from typing import List, Optional

import typer
from typing_extensions import Annotated

from abacus.core import AbacusError
from abacus.typer_cli.base import UserChart, last

chart = typer.Typer(help="Modify chart of accounts.", add_completion=False)


def assure_chart_file_exists(chart_file=None):
    path = UserChart.default()._path if chart_file is None else chart_file
    if not path.exists():
        sys.exit(
            f"Chart file ({path}) not found. Use `chart init` command to create it."
        )


@chart.command()
def init():
    """Initialize chart file in current directory."""
    path = UserChart.default()._path
    if path.exists():
        print(f"Chart file ({path}) already exists.")
    else:
        UserChart.default().save()
        print(f"Created chart file: {path}")


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
    chart_file: Optional[Path] = None,
):
    """Add accounts to chart."""
    if len(labels) == 1 and title:
        name(last(labels[0]), title)
    user_chart = UserChart.load(chart_file)
    match [asset, capital, liability, income, expense].count(True):
        case 0:
            user_chart.use(*labels).save()
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
            try:
                user_chart.use(*labels, prefix=prefix).save()
            except AbacusError as e:
                sys.exit(str(e))
            print(f"Added accounts ({prefix}):", spaced(labels))
        case _:
            sys.exit("Use only one or no flags.")


@chart.command()
def set(
    income_summary_account: Optional[str] = None,
    retained_earnings_account: Optional[str] = None,
    null_account: Optional[str] = None,
    chart_file: Optional[Path] = None,
):
    """Set income summary, retained earnings or null accounts."""
    if not (income_summary_account or retained_earnings_account or null_account):
        sys.exit("No changes made.")
    user_chart = UserChart.load(chart_file)
    if income_summary_account:
        user_chart.set_isa(income_summary_account)
        print(f"New income summary account is {income_summary_account}.")
    if retained_earnings_account:
        user_chart.set_re(retained_earnings_account)
        print(f"New retained earnings account is {retained_earnings_account}.")
    if null_account:
        user_chart.set_null(null_account)
        print(f"New null account is {null_account}.")
    user_chart.save()


@chart.command()
def name(account_name: str, title: str, chart_file: Optional[Path] = None):
    """Set account title."""
    user_chart = UserChart.load(chart_file)
    user_chart.name(account_name, title).save()
    print(f"New title for {account_name} is {title}.")


@chart.command()
def offset(name: str, contra_names: list[str], chart_file: Optional[Path] = None):
    """Add contra accounts."""
    user_chart = UserChart.load(chart_file)
    for contra_name in contra_names:
        try:
            user_chart.offset(name, contra_name)
        except AbacusError:
            sys.exit(str())
    user_chart.save()
    s = "" if len(contra_names) == 1 else "s"
    print(f"Added contra account{s} for {name}:", spaced(contra_names))


@chart.command()
def show(chart_file: Optional[Path] = None):
    """Print chart."""
    assure_chart_file_exists(chart_file)
    print(UserChart.load(chart_file).json(indent=4, ensure_ascii=False))


@chart.command()
def unlink(
    yes: Annotated[bool, typer.Option(prompt="Are you sure you want to chart file?")]
):
    """Permanently delete chart file in current directory."""

    if yes:
        UserChart.default()._path.unlink(missing_ok=True)
