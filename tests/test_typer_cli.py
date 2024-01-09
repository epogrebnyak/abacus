from typer.testing import CliRunner
from pathlib import Path

from abacus.typer_cli import app

runner = CliRunner()


def test_about():
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "abacus" in result.stdout

def test_init():
    with runner.isolated_filesystem() as f:
        result = runner.invoke(app, ["init", "ABC Company"])
        assert result.exit_code == 0
        assert (Path(f) / "chart.json").exists()
        assert (Path(f) / "entries.linejson").exists()
        assert "Created chart file:" in result.stdout
        assert "Created entries file:" in result.stdout

def test_unlink_deletes_files():
    with runner.isolated_filesystem() as f:
        runner.invoke(app, ["init", "ABC Company"])
        runner.invoke(app, ["unlink", "--yes"])
        assert not (Path(f) / "chart.json").exists()
        assert not (Path(f) / "entries.linejson").exists()


