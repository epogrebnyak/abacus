import os
from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import click
from tomli import loads
from tomli_w import dump  # type: ignore

default_config_filename = "abacus.toml"


@dataclass
class Location:
    """Working directory and configuration file name ('abacus.toml' by default)."""

    folder: Path
    config_filename: str = default_config_filename

    @property
    def config_path(self) -> Path:
        return self.folder / self.config_filename


def get_cli_options(location: Location) -> Dict:
    return TOML(path=location.config_path).load()["abacus"]["options"]


@dataclass
class TOML(UserDict):
    """TOML as dictionary with save() and load() methods."""

    path: Path

    def load(self):
        self.data = loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def save(self):
        self.path.write_text(dump(self.data), encoding="utf-8")


option_folder = click.option(
    "--folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=False,
        readable=True,
        resolve_path=True,
        allow_dash=False,
        path_type=Path,
        executable=False,
    ),
    default=os.getcwd(),
    help=f"Project folder with {default_config_filename} and data files [default: .]",
)
option_config_filename = click.option(
    "--config-filename",
    default=default_config_filename,
    help=f"Configuration file name  [default: {default_config_filename}]",
)


@click.group()
@option_folder
@option_config_filename
@click.pass_context
def entry_point(ctx, folder, config_filename):
    # pass next further with @click.pass_obj decorator
    ctx.obj = Location(folder, config_filename)


@entry_point.command(
    name="add-accounts",
    help="Add accounts to chart.",
)
@click.option("--chart")
@click.option("--assets")
def add_accounts(chart, assets):
    click.echo(chart, assets)


@entry_point.command(
    name="chart",
    help="Create chart of accounts.",
)
@click.option("-a", "--assets", required=True)
@click.option("-e", "--expenses", required=True)
@click.option("-c", "--capital", required=True)
@click.option("-r", "--retained_earnings", required=True)
@click.option("-l", "--liabilities", required=True)
@click.option("-i", "--income", required=True)
@click.option("-n", "--contra-account", nargs=3, multiple=True)
def chart(
    assets, expenses, capital, retained_earnings, liabilities, income, contra_account
):
    click.echo(
        [
            assets,
            expenses,
            capital,
            retained_earnings,
            liabilities,
            income,
            contra_account,
        ]
    )


@entry_point.command(name="post", help="Post entry to general ledger.")
@click.option("--dr", required=True)
@click.option("--cr", required=True)
@click.option("--amount", required=True)
@click.pass_obj
def post_entry(location, dr, cr, amount):
    click.echo([location, dr, cr, amount])


@entry_point.command(name="close", help="Close accounts at period end.")
@click.option("--all", "all_")
@click.pass_obj
def close(location, all_):
    click.echo([location, all_])


@entry_point.command(name="report", help="Create financial report.")
@click.option(
    "--income-statement",
    "-i",
    "report",
    flag_value="income_statement",
    help="Create income statement.",
)
@click.option(
    "--balance-sheet",
    "-b",
    "report",
    flag_value="balance_sheet",
    help="Create balance sheet.",
)
@click.option("--console", "output", flag_value="console", default=True)
@click.option("--json", "output", flag_value="json")
@click.pass_obj
def report(ctx, report, output):
    match report:
        case "income_statement":
            click.echo([report, output])
        case "balance_sheet":
            click.echo([report, output])


@entry_point.command(
    name="show-config-file-options", help="Show options from configuration file."
)
@click.pass_obj
def config_file(location):
    click.echo(get_cli_options(location))


if __name__ == "__main__":
    entry_point()
