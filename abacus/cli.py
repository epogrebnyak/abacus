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
    default=os.getcwd(),
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
    # pass next further with @click.pass_obj decorator
    ctx.obj = Location(folder, config_filename)


@entry_point.command(help="Show options from configuration file.")
@click.pass_obj
def config(location):
    click.echo(get_cli_options(location))


if __name__ == "__main__":
    entry_point()
