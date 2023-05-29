from pathlib import Path

import pytest


def write_toml(folder):
    return touch(
        folder,
        "abacus.toml",
        """[abacus.options]
chart = "chart.json"
start = "start_balances.json" 
entries = "entries.json"
rename = "rename.json"
""",
    )


def touch(directory, filename: str, content: str):
    path = Path(directory) / filename
    path.write_text(content)
    return str(path)


def test_with_runner(script_runner, tmp_path):
    write_toml(tmp_path)
    result = script_runner.run(["abacus", "--project-folder", str(tmp_path), "fire"])
    assert result.returncode == 0
    assert (
        result.stdout
        == "{'chart': 'chart.json', 'start': 'start_balances.json', 'entries': 'entries.json', 'rename': 'rename.json'}\n"
    )
    assert result.stderr == ""
    result.print()


lines = """abacus --project-folder {tmp_path} fire 
abacus --project-folder {tmp_path} chart -a cash,goods,ppe -e cogs,sga,rent,interest -c eq -r re -l dividend_due,loan -i sales -n sales discounts,cashback net_sales -n eq treasury_stock free_float -n ppe depreciation net_ppe
abacus --project-folder {tmp_path} post --dr cash --cr eq --amount 1500 --store {store_path} 
abacus --project-folder {tmp_path} post --dr goods --cr cash --amount 900 --store {store_path}
abacus --project-folder {tmp_path} post --dr cash --cr sales --amount 680 --store {store_path}
abacus --project-folder {tmp_path} post --dr cogs --cr goods --amount 500 --store {store_path}
abacus --project-folder {tmp_path} post --dr discounts --cr cash --amount 15 --store {store_path}
abacus --project-folder {tmp_path} post --dr cashback --cr cash --amount 15 --store {store_path}
abacus --project-folder {tmp_path} close --all
abacus --project-folder {tmp_path} report --income-statement
abacus --project-folder {tmp_path} report --balance-sheet""".split(
    "\n"
)


@pytest.mark.parametrize("line", lines)
def test_cli_runner(script_runner, tmp_path, line):
    write_toml(tmp_path)
    store_path = touch(tmp_path, "entries.json", '{"postings": []}')
    command = line.format(store_path=store_path, tmp_path=str(tmp_path))
    result = script_runner.run(command.split())
    assert result.returncode == 0
