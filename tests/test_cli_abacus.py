import pathlib
import subprocess

import pytest  # type: ignore


@pytest.fixture
def commands():
    path = pathlib.Path(__file__).parent / "test_cli_abacus.sh"
    return [
        line
        for line in path.read_text().split("\n")
        if line and not line.startswith("#")
    ]


def test_few_commands_abacus(commands, tmpdir):
    for command in commands:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, cwd=tmpdir
        )
        assert result.returncode == 0
    # # final check
    # assert json.loads(result.stdout) == {
    #     "cash": 200,
    #     "goods": 800,
    #     "equity": 1000,
    # }
