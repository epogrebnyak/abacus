from pathlib import Path
from shlex import split

import pytest
from typer.testing import CliRunner

from abacus.typer_cli import app

runner = CliRunner()

@pytest.mark.cli
@pytest.mark.parametrize(
    "word", ["assert", "chart", "init", "ledger", "report", "show", "unlink"]
)
def test_help(word):
    result = runner.invoke(app, ["--help"])
    assert word in result.stdout


@pytest.mark.cli
def test_init_creates_files():
    with runner.isolated_filesystem() as f:
        a = Path(f) / "chart.json"
        b = Path(f) / "entries.linejson"
        result = runner.invoke(app, ["init", "--company-name='ABC Company'"])
        assert result.exit_code == 0
        assert a.exists()
        assert b.exists()
        assert "Created chart file:" in result.stdout
        assert "Created entries file:" in result.stdout
        assert "ABC Company" in a.read_text()


@pytest.mark.cli
def test_unlink_deletes_files():
    with runner.isolated_filesystem() as f:
        a = Path(f) / "chart.json"
        b = Path(f) / "entries.linejson"
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert a.exists()
        assert b.exists()
        result = runner.invoke(app, ["unlink", "--yes"])
        assert result.exit_code == 0
        assert not a.exists()
        assert not b.exists()


chart_script = """chart init 
chart add -a cash ar paper
chart add -c equity
chart add --liability loan 
chart add income:sales expense:salaries,interest
chart add contra:equity:ts --title "Treasury stock"
chart name paper "Inventory (paper products)"
chart offset sales refunds voids
chart show --json"""


@pytest.mark.parametrize("script", [chart_script])
@pytest.mark.cli
def test_scripts(script):
    with runner.isolated_filesystem():
        for line in script.split("\n"):
            result = runner.invoke(app, split(line))
            assert result.exit_code == 0
