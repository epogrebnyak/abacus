# print(sys.path)
# print(os.path.realpath(__file__))
# print(os.path.realpath("./"))
# print(os.getcwd())
# also: https://github.com/gitpython-developers/GitPython/blob/6fc11e6e36e524a6749e15046eca3a8601745822/git/cmd.py#L714C49-L725

import os
from tomli import loads
from tomli_w import dump
from pathlib import Path
from dataclasses import dataclass
from collections import UserDict
from typing import Dict

import click

default_config_filename = "abacus.toml"


@dataclass
class Location:
    """Working directory and configuration file name (like 'abacus.toml')."""

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
    default=os.getcwd(),  # or os.path.abspath('.')
    help=f"Project folder with {default_config_filename} and data files [default: ./]",
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
    # pass next further with click.pass_obj decorator
    ctx.obj = Location(folder, config_filename)


@entry_point.command(help="Show options from configuration file.")
@click.pass_obj
def config(location):
    click.echo(get_cli_options(location))


if __name__ == "__main__":
    entry_point()
