import json
import subprocess
import os


import pytest


@pytest.fixture
def commands():
    return """
jaba chart chart.json touch
jaba chart chart.json set --assets cash goods
jaba chart chart.json set --capital equity
jaba chart chart.json set --retained-earnings re
jaba chart chart.json make store.json
jaba ledger store.json post cash equity 1000
jaba ledger store.json post goods cash 300
jaba balances store.json show --skip-zero --json""".strip()



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
        if os.name == "nt":
            command = line.replace("jaba", "python -m abacus.jaba").split()
        else:
            command = line
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
    # final check
    assert json.loads(result.stdout) == {
        "cash": 700,
        "goods": 300,
        "equity": 1000,
    }
