from typer.testing import CliRunner

from abacus.typer_cli import app

runner = CliRunner()


def test_about():
    result = runner.invoke(app, ["about"])
    assert result.exit_code == 0
    assert "abacus" in result.stdout
