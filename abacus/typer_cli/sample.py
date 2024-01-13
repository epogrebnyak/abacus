import click
import typer

app = typer.Typer()


@app.command()
def top():
    """
    Top level command, form Typer
    """
    print("The Typer app is at the top level")


@app.callback()
def callback():
    """
    Typer app, including Click subapp
    """


@click.command()
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(name):
    """Simple program that greets NAME for a total of COUNT times."""
    click.echo("Hello %s!" % name)


typer_click_object = typer.main.get_command(app)

typer_click_object.add_command(hello, "hello")

from typer.testing import CliRunner

typer_click_object._add_completion = False
typer_click_object.registered_callback = lambda x: ...
typer_click_object.pretty_exceptions_short = []
# AttributeError: 'TyperGroup' object has no attribute 'registered_commands'

runner = CliRunner()
runner.invoke(typer_click_object, ["hello", "--name", "Camila"])
print(runner)

"""
/home/codespace/.python/current/bin/python3 /workspaces/abacus/abacus/typer_cli/sample.py
Traceback (most recent call last):
  File "/workspaces/abacus/abacus/typer_cli/sample.py", line 36, in <module>
    runner.invoke(typer_click_object, ["hello", "--name", "Camila"])
  File "/home/codespace/.python/current/lib/python3.10/site-packages/typer/testing.py", line 20, in invoke
    use_cli = _get_command(app)
  File "/home/codespace/.python/current/lib/python3.10/site-packages/typer/main.py", line 341, in get_command
    if typer_instance._add_completion:
AttributeError: 'TyperGroup' object has no attribute '_add_completion'
"""
