from pathlib import Path

from click.testing import CliRunner

from abacus.cli import entry_point


def test_options_command(tmpdir):
    runner = CliRunner()
    with runner.isolated_filesystem(tmpdir):
        toml_content = """
[abacus.options]
chart = "chart.json"
start_balances = "start_balances.json" 
entries = "entries.json"
"""
        (Path(tmpdir) / "abc.toml").write_text(toml_content)
        result = runner.invoke(
            entry_point,
            f"--folder {tmpdir} --config-filename abc.toml show-config-file-options",
        )
        assert result.exit_code == 0
        assert (
            result.output
            == "{'chart': 'chart.json', 'start_balances': 'start_balances.json', 'entries': 'entries.json'}\n"
        )
