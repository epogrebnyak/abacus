import json
import subprocess

import pytest


@pytest.fixture
def commands():
    return """
jaba chart chart.json touch
jaba chart chart.json set --assets cash goods
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba store store.json init chart.json
jaba store store.json post cash equity 1000
jaba store store.json post goods cash 300
jaba balances store.json end
""".strip()


def make_args(command: str) -> list[str]:
    return command.replace("jaba", "python -m abacus.jaba").split()


def test_n_commands(commands):
    assert len(commands.split("\n")) == 8


def test_runner(tmpdir):
    result = subprocess.run(["python", "--version"], cwd=tmpdir)
    assert result.returncode == 0


def test_run_one(tmpdir):
    result = subprocess.run(
        "python -m abacus.jaba --help".split(), shell=True, cwd=tmpdir
    )
    assert result.returncode == 0


def test_few_commands(commands, tmpdir):
    for line in commands.split("\n"):
        result = subprocess.run(
            make_args(line), shell=True, capture_output=True, cwd=tmpdir
        )
        assert result.returncode == 0
    assert json.loads(result.stdout.decode()) == {
        "cash": 700,
        "goods": 300,
        "equity": 1000,
    }
