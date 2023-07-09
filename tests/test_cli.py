import json
import pathlib
import subprocess

import pytest


@pytest.fixture
def commands():
    path = pathlib.Path(__file__).parent / "test_cli.bat"
    return path.read_text().replace("|| exit /b", "").strip()


def test_n_commands(commands):
    assert len(commands.split("\n")) == 16


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
