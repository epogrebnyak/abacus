import json
import subprocess

import pytest


@pytest.fixture
def commands():
    return """
bx chart set --asset cash 
bx chart set --asset goods
bx chart set --capital equity
bx chart set --retained-earnings re
bx ledger start
bx ledger post --debit cash --credit equity --amount 1000
bx ledger post --debit goods --credit cash --amount 800
bx assert equity 1000
bx assert cash 200
bx assert goods 800
bx show balances --json
""".strip()


def test_n_commands(commands):
    assert len(commands.split("\n")) == 11


def test_runner(tmpdir):
    result = subprocess.run(["python", "--version"], cwd=tmpdir)
    assert result.returncode == 0


def test_run_bx_help(tmpdir):
    result = subprocess.run(
        "python -m abacus.bx --help".split(), shell=True, cwd=tmpdir
    )
    assert result.returncode == 0


def test_few_commands(commands, tmpdir):
    for line in commands.split("\n"):
        # if os.name == "nt":
        #    command = line.replace("jaba", "python -m abacus.jaba").split()
        # else:
        command = line
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
    # final check
    assert json.loads(result.stdout) == {
        "cash": 200,
        "goods": 800,
        "equity": 1000,
    }
