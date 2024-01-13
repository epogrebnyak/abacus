from dataclasses import dataclass, field
from pathlib import Path
from shlex import split

import pytest
from typer.testing import CliRunner

from abacus.typer_cli.app import combined_typer_click_app as app
from abacus.typer_cli.base import UserChartCLI
from abacus.user_chart import AccountLabel, T

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


@dataclass
class Setting:
    script: str
    user_chart_dict: dict | None = None
    exit_code: int = 0


chart_setting = Setting(
    """
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
chart show --json
""",
    user_chart_dict={
        "account_labels": {
            "ar": AccountLabel(type=T.Asset, contra_names=[]),
            "cash": AccountLabel(type=T.Asset, contra_names=[]),
            "equity": AccountLabel(type=T.Capital, contra_names=["ts"]),
            "interest": AccountLabel(type=T.Expense, contra_names=[]),
            "loan": AccountLabel(type=T.Liability, contra_names=[]),
            "paper": AccountLabel(type=T.Asset, contra_names=[]),
            "salaries": AccountLabel(type=T.Expense, contra_names=[]),
            "sales": AccountLabel(type=T.Income, contra_names=["refunds", "voids"]),
        },
        "company_name": None,
        "income_summary_account": "new_re",
        "null_account": "new_null",
        "rename_dict": {"paper": "Inventory (paper products)", "ts": "Treasury stock"},
        "retained_earnings_account": "new_isa",
    },
)


@pytest.mark.parametrize("setting", [chart_setting])
@pytest.mark.cli
def test_script_as_setting(setting):
    with runner.isolated_filesystem() as f:
        for line in setting.script.split("\n"):
            if line:
                result = runner.invoke(app, split(line))
                assert result.exit_code == setting.exit_code
        if setting.user_chart_dict is not None:
            uci = UserChartCLI.load(f)
            assert uci.user_chart.dict() == setting.user_chart_dict


@dataclass
class Line:
    script: str
    comment: str | None = None
    stdout_contains: list[str] = field(default_factory=list)

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


def all_happy(script: str):
    return [HappyLine(line) for line in script.split("\n") if line]


@pytest.mark.parametrize(
    "lines",
    [
        [HappyLine("chart init"), SadLine("chart set")],
        [SadLine("chart set --income-summary-account new_isa")],
        [SadLine("chart unlink --yes")],
        [HappyLine("chart init"), HappyLine("chart unlink --yes")],
        [HappyLine("ledger init")],
        [SadLine("ledger unlink --yes")],
        [HappyLine("ledger init"), HappyLine("ledger unlink --yes")],
        [HappyLine(
            "post --entry asset:cash capital:eq 1000 --credit income:sales 50 --credit liability:vat 10 --debit asset:ar 60 --strict"
        ).prints("True").prints("income:sales")
        ],
        all_happy(
            """
chart init
ledger init 
ledger post     asset:cash capital:equity 49 
ledger post cash equity 51 
"""
        ),
    ],
)
@pytest.mark.cli
def test_by_line(lines):
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
        assert "Created entries file:" in result.stdout
        result = runner.invoke(app, ["ledger", "unlink", "--yes"])
        assert result.exit_code == 0
        assert not b.exists()
