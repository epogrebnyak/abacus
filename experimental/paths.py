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

import click

default_folder = Path(os.getcwd())  # or Path(os.path.abspath('.')
default_config_filename = "abacus.toml"


@dataclass
class Location:
    folder: str = default_folder
    config_filename: str = default_config_filename

    @property
    def folder_path(self) -> Path:
        return Path(self.folder)

    @property
    def config_path(self) -> Path:
        return self.folder_path / self.config_filename


def get_cli_options(location: Location):
    return TOML(path=location.config_path).load()["abacus"]["options"]


@dataclass
class TOML(UserDict):
    path: Path

    def load(self):
        self.data = loads(self.path.read_text(encoding="utf-8"))
        return self.data

    def save(self):
        self.path.write_text(dump(self.data), encoding="utf-8")


option_folder = click.option(
    "--folder",
    default=str(default_folder),
    help=f"Project folder with {default_config_filename} and data files [default: ./]",
)
option_config_filename = click.option(
    "--config-filename",
    default=default_config_filename,
    help="Path to configuration file [default: ./abacus.toml]",
)


@click.group()
@option_folder
@option_config_filename
def cli(folder, config_filename):
    # click.echo("Hello!")
    pass


@cli.command(help="Show options from configuration file.")
@option_folder
@option_config_filename
def options(folder, config_filename):
    location = Location(folder, config_filename)
    from_config_file_options = get_cli_options(location)
    click.echo(str(from_config_file_options))


if __name__ == "__main__":
    cli()
