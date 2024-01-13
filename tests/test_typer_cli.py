import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from shlex import split

import pytest
from typer.testing import CliRunner

from abacus.typer_cli.app import app

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
        result = runner.invoke(app, ["init"])
        assert result.exit_code == 0
        assert a.exists()
        assert b.exists()
        assert "Created chart" in result.stdout
        assert "Created empty ledger" in result.stdout


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


@dataclass
class Setting:
    script: str
    user_chart_dict: dict | None = None
    exit_code: int = 0


chart_setting = """
chart init 
chart add -a cash ar paper
chart add -c equity
chart add --liability loan 
chart add income:sales expense:salaries,interest
chart add contra:equity:ts --title "Treasury stock"
chart name paper "Inventory (paper products)"
chart offset sales refunds voids
chart set --retained-earnings-account new_isa --income-summary-account new_re --null-account new_null
chart show
"""


@pytest.mark.parametrize("setting", [chart_setting])
@pytest.mark.cli
def test_script_as_setting(setting):
    runner = CliRunner()
    with runner.isolated_filesystem():
        for line in setting.split("\n"):
            if line:
                result = runner.invoke(app, split(line))
                assert result.exit_code == 0


@dataclass
class Line:
    script: str
    comment: str | None = None
    stdout_contains: list[str] = field(default_factory=list)

    @property
    def exit_code(self):
        match self:
            case HappyLine(_, _):
                return 0
            case SadLine(_, _):
                return 1

    @property
    def args(self):
        return split(self.script)

    def prints(self, s: str):
        self.stdout_contains.append(s)
        return self


class HappyLine(Line):
    ...


class SadLine(Line):
    ...


def assert_subprocess(command: str, line: Line):
    args = [command] + line.args
    result = subprocess.run(args, text=True, capture_output=True)
    print
    print(result.stdout)
    print(result.stderr)
    assert result.returncode == line.exit_code
    for s in line.stdout_contains:
        assert s in result.stdout


@pytest.mark.skip
def test_post_zzz():
    h = (
        HappyLine(
            "post --entry asset:cash capital:eq 1000 --credit income:sales 50 --credit liability:vat 10 --debit asset:ar 60"
        )
        .prints("Posted")
        .prints("sales")
    )
    assert_subprocess("bx", h)


def all_happy(script: str):
    return [HappyLine(line) for line in script.split("\n") if line]


@pytest.mark.parametrize(
    "lines",
    [
        [HappyLine("chart init"), SadLine("chart set")],
        [SadLine("chart set --income-summary-account new_isa")],
        [HappyLine("chart unlink --yes")],
        [HappyLine("chart init"), HappyLine("chart unlink --yes")],
        [HappyLine("ledger init")],
        [HappyLine("ledger unlink --yes")],
        [HappyLine("ledger init"), HappyLine("ledger unlink --yes")],
        all_happy(
            """
chart init
ledger init 
ledger post asset:cash capital:equity 49 
ledger post cash equity 51 
"""
        ),
    ],
)
@pytest.mark.cli
def test_by_line(lines):
    runner = CliRunner()
    with runner.isolated_filesystem():
        for line in lines:
            print(line)
            print(line.args)
            result = runner.invoke(app, line.args)
            print(result.stdout)
            match line:
                case HappyLine(_, _):
                    assert result.exit_code == 0
                case SadLine(_, _):
                    assert result.exit_code == 1
            if line.stdout_contains:
                for s in line.stdout_contains:
                    assert s in result.stdout


@pytest.mark.cli
def test_ledger_create_and_delete_files():
    with runner.isolated_filesystem() as f:
        b = Path(f) / "entries.linejson"
        result = runner.invoke(app, ["ledger", "init"])
        assert result.exit_code == 0
        assert b.exists()
        assert "Created empty ledger file" in result.stdout
        result = runner.invoke(app, ["ledger", "unlink", "--yes"])
        assert result.exit_code == 0
        assert not b.exists()
