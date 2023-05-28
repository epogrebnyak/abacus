from pathlib import Path

from click.testing import CliRunner

from abacus.cli import entry_point


def write_toml(folder):
    path = Path(folder) / "abacus.toml"
    path.write_text(
        """
[abacus.options]
chart = "chart.json"
start_balances = "start_balances.json" 
entries = "entries.json"
"""
    )
    return str(path)


def test_options_command(tmpdir):
    runner = CliRunner()
    with runner.isolated_filesystem(tmpdir):
        write_toml(tmpdir)
        result = runner.invoke(
            entry_point,
            f"--folder {tmpdir} show-config-file-options",
        )
        assert result.exit_code == 0
        assert (
            result.output
            == "{'chart': 'chart.json', 'start_balances': 'start_balances.json', 'entries': 'entries.json'}\n"
        )

def touch(tmpdir, filename: str, content: str):
    path = Path(tmpdir) / filename
    path.write_text(content)
    return str(path)

def test_cli(tmpdir):
    runner = CliRunner()
    with runner.isolated_filesystem(tmpdir):
        write_toml(tmpdir)
        store_path = touch(tmpdir, "entries.json", "{\"postings\": []}")
        commands = """abacus show-config-file-options 
abacus chart -a cash,goods,ppe -e cogs,sga,rent,interest -c eq -r re -l dividend_due,loan -i sales -n sales discounts,cashback net_sales -n eq treasury_stock free_float -n ppe depreciation net_ppe

abacus post --dr cash --cr eq --amount 1500 --store {store_path} 
abacus post --dr goods --cr cash --amount 900 --store {store_path}
abacus post --dr cash --cr sales --amount 680 --store {store_path}
abacus post --dr cogs --cr goods --amount 500 --store {store_path}
abacus post --dr discounts --cr cash --amount 15 --store {store_path}
abacus post --dr cashback --cr cash --amount 15 --store {store_path}
abacus close --all
abacus report --income-statement --console
abacus report --balance-sheet --json""".format(store_path=store_path)
        for command in commands.split("\n"):
            command = command.replace("abacus ", f"--folder {tmpdir} ")
            result = runner.invoke(entry_point, command)
            assert result.exit_code == 0
