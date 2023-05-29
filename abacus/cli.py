import os
from collections import UserDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import click  # type: ignore
from tomli import loads
from tomli_w import dump  # type: ignore

from abacus import Chart
from abacus.store import Entries

default_config_filename = "abacus.toml"


def config_path(directory: str, filename: str) -> Path:
    return Path(directory) / filename


@dataclass
class Location:
    """Working directory and configuration file name ('abacus.toml' by default)."""

    folder: str
    config_filename: str = default_config_filename

    @property
    def config_path(self) -> Path:
        return Path(self.folder) / self.config_filename


def get_cli_options(config: Dict) -> Dict:
    return config["abacus"]["options"]


def load_toml(path: Path):
    return loads(path.read_text(encoding="utf-8"))


@dataclass
class TOML(UserDict):
    """TOML as dictionary with save() and load() methods."""

    path: Path

    def load(self):
        self.data = loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def save(self):
        self.path.write_text(dump(self.data), encoding="utf-8")


@click.group()
@click.option(
    "--project-folder",
    default=os.getcwd(),
    help=f"Project folder with {default_config_filename} and data files [default: .]",
)
@click.option(
    "--config-filename",
    default=default_config_filename,
    help=f"Configuration file name  [default: {default_config_filename}]",
)
@click.pass_context
def entry_point(ctx, project_folder, config_filename):
    # pass next further with @click.pass_obj decorator
    path = config_path(project_folder, config_filename)
    ctx.obj = load_toml(path)


@entry_point.command(name="fire", help="Show options from configuration file.")
@click.pass_obj
def config_file(config):
    click.echo(config["abacus"]["options"])


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
@click.option("-s", "--income-summary-account", default="_profit")
@click.option("-n", "--contra-accounts", nargs=3, multiple=True)
def chart(**kwargs):
    click.echo(make_chart(**kwargs).json())


def to_dict(tuples):
    return {
        name: (contra_accounts.split(","), resulting_name)
        for (name, contra_accounts, resulting_name) in tuples
    }


def make_chart(**kwargs):
    return Chart(
        assets=kwargs["assets"].split(","),
        expenses=kwargs["expenses"].split(","),
        equity=kwargs["capital"].split(","),
        liabilities=kwargs["liabilities"].split(","),
        income=kwargs["income"].split(","),
        retained_earnings_account=kwargs["retained_earnings"],
        income_summary_account=kwargs["income_summary_account"],
        contra_accounts=to_dict(kwargs["contra_accounts"]),
    )


@entry_point.group()
def empty():
    pass


@empty.command(name="store", help="Create empty store for posting entries.")
def empty_store():
    click.echo(Entries(postings=[]).json())


store_option = click.option(
    "--store",
    required=True,
)


@entry_point.command(name="post", help="Post entry to general ledger.")
@click.option("--dr", required=True)
@click.option("--cr", required=True)
@click.option("--amount", required=True)
@store_option
@click.pass_obj
def post_entry(location, dr, cr, amount, store):
    entries = Entries.parse_file(store)
    entries.add_entry(dr, cr, amount)
    entries.save(store)
    click.echo(entries.postings)


@entry_point.command(name="close", help="Close accounts at period end.")
@click.option("--all", "all_", is_flag=True)
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


if __name__ == "__main__":
    entry_point()
