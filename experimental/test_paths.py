from pathlib import Path
from click.testing import CliRunner
from paths import cli


def test_options_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        toml_content = """
[abacus.options]
chart = "chart.json"
start_balances = "start_balances.json" 
entries = "entries.json"
"""
        Path("abc.toml").write_text(toml_content)
        result = runner.invoke(cli, "options", "--config-filename abc.toml")
        # assert result.exit_code == 0
        assert (
            result.output
            == "{'chart': 'chart.json', 'start_balances': 'start_balances.json', 'entries': 'entries.json'}\n"
        )
