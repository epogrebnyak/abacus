from pathlib import Path

import pytest
from typer.testing import CliRunner

from abacus.typer_cli import app

runner = CliRunner()


def test_about():
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "abacus" in result.stdout


@pytest.mark.parametrize(
    "word", ["about", "assert", "chart", "ledger", "report", "show", "unlink"]
)
def test_help(word):
    result = runner.invoke(app, ["--help"])
    assert word in result.stdout


def test_init():
    with runner.isolated_filesystem() as f:
        result = runner.invoke(app, ["init", "--company-name='ABC Company'"])
        assert result.exit_code == 0
        assert (Path(f) / "chart.json").exists()
        assert (Path(f) / "entries.linejson").exists()
        assert "Created chart file:" in result.stdout
        assert "Created entries file:" in result.stdout
        assert "ABC Company" in (Path(f) / "chart.json").read_text()


def test_unlink_deletes_files():
    with runner.isolated_filesystem() as f:
        runner.invoke(app, ["init", "ABC Company"])
        runner.invoke(app, ["unlink", "--yes"])
        assert not (Path(f) / "chart.json").exists()
        assert not (Path(f) / "entries.linejson").exists()
