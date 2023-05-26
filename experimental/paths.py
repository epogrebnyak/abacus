import os
import sys

# --project-folder and --config options

import click
from pathlib import Path


default_project_folder = Path(os.getcwd())
default_config_file = default_project_folder / "abacus.toml"

print("sys.path:", sys.path)
print("__file__:", os.path.realpath(__file__))
print("./", os.path.realpath("./"))
print("os.getcwd():", os.getcwd())


@click.command()
@click.option(
    "--project-folder",
    default=default_project_folder,
    help="Project folder with configuration and data files (default is ./)",
)
@click.option(
    "--config",
    default=default_config_file,
    help="Path to configuration file (default is ./abacus.toml)",
)
def hello(project_folder, config):
    click.echo(f"--project-folder default: {default_project_folder}")
    click.echo(f"--project-folder:         {project_folder}")
    click.echo(f"--config default:         {default_config_file}")
    click.echo(f"        --config:         {config}")


# todo: if project folder is specified and config is a file and not a Path with directory, concat project folder
# https://github.com/gitpython-developers/GitPython/blob/6fc11e6e36e524a6749e15046eca3a8601745822/git/cmd.py#L714C49-L725

if __name__ == "__main__":
    hello()
