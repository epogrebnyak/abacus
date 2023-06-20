"""Double entry accounting manager.

Usage:
  bx init
  bx chart set --assets <account_names>...
  bx chart set --capital <account_names>...
  bx chart set --retained-earnings <account_name>
  bx chart set --liabilities <account_names>...
  bx chart set --income <account_names>...
  bx chart set --expenses <account_names>... 
  bx chart offset <account> (--contra-accounts <contra_accounts>...)
  bx chart offset <account> <contra_accounts>...
  bx chart show
  bx ledger start [--file <balances_file>] [--dry-run]
  bx ledger post --debit <dr> --credit <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post --dr <dr> --cr <cr> --amount <amount> [--adjust] [--post-close]
  bx ledger post <dr> <cr> <amount> [--adjust] [--post-close]
  bx ledger close
  bx name <account_name> <title>
  bx name <account_name> ((-t | --title) <title>)
  bx report (-i | --income-statement) 
  bx report (-b | --balance-sheet) 
  bx report (-t | --trial-balance)
  bx balances (--nonzero | --all)
  bx balances <account_name> [--assert <amount>]
  bx end
  bx debug --args

Options:
  -h --help     Show this help message.
  --version     Show version.
"""

from docopt import docopt


def init():
    # Implementation for "bx init"
    pass


def chart_set_assets():
    # Implementation for "bx chart set"
    pass


def chart_set_capital():
    # Implementation for "bx chart set"
    pass


def chart_set_liabilities():
    # Implementation for "bx chart set"
    pass


def chart_set_income():
    # Implementation for "bx chart set"
    pass


def chart_set_expenses():
    # Implementation for "bx chart set"
    pass


def chart_set_retained_earnings():
    # Implementation for "bx chart set --retained_earnings"
    pass


def chart_offset(account, contra_accounts):
    # Implementation for "bx chart offset"
    pass

def chart_show():
    pass


def ledger_start(file, dry_run):
    # Implementation for "bx ledger start"
    pass


def ledger_post(dr, cr, amount, adjust, post_close):
    # Implementation for "bx ledger post"
    pass


def ledger_close():
    # Implementation for "bx ledger close"
    pass


def name(account_name, title):
    # Implementation for "bx name"
    pass


def report_income_statement():
    """Implementation for 'bx report -i'"""
    print("i")


def report_balance_sheet():
    """Implementation for 'bx report -b'"""
    print("b")


def report_trial_balance():
    """Implementation for 'bx report -t'"""
    print("t")


def account_balance(account_name: str):
    print(account_name)


def assert_account_balance(account_name: str, assert_amount: str):
    print(account_name, assert_amount)


def balances(all_flag: bool, nonzero_flag: bool, json: bool = False):
    print(all_flag, nonzero_flag)


def end():
    # Implementation for "bx end"
    pass


def debug(arguments):
    # Implementation for "bx debug"
    print(arguments)


def main():
    arguments = docopt(__doc__, version="0.4.13")

    # Call the corresponding functions based on the command and options
    if arguments["init"]:
        init()
    elif arguments["debug"]:
        debug(arguments)
    elif arguments["chart"] and arguments["set"]:
        account_names = arguments["<account_names>"]
        if arguments["--assets"]:
            chart_set_assets(account_names)
        elif arguments["--capital"]:
            chart_set_capital(account_names)
        elif arguments["--liabilities"]:
            chart_set_liabilities(account_names)
        elif arguments["--income"]:
            chart_set_income(account_names)
        elif arguments["--expenses"]:
            chart_set_expenses(account_names)
        elif arguments["--retained-earnings"]:
            chart_set_retained_earnings(arguments["account_name"])
    elif arguments["chart"] and arguments["offset"]:
        chart_offset(arguments["<account>"], arguments["<contra_accounts>"])
    elif arguments["chart"] and arguments["show"]:
        chart_show()
    elif arguments["ledger"] and arguments["start"]:
        ledger_start(arguments["--file"], arguments["--dry-run"])
    elif arguments["ledger"] and arguments["post"]:
        ledger_post(
            arguments["<dr>"],
            arguments["<cr>"],
            arguments["<amount>"],
            arguments["--adjust"],
            arguments["--post-close"],
        )
    elif arguments["ledger"] and arguments["close"]:
        ledger_close()
    elif arguments["name"]:
        name(arguments["<account_name>"], arguments["<title>"])
    elif arguments["report"]:
        if arguments["-i"] or arguments["--income-statement"]:
            report_income_statement()
        elif arguments["-b"] or arguments["--balance-sheet"]:
            report_balance_sheet()
        elif arguments["-t"] or arguments["--trail-balance"]:
            report_trial_balance()
    elif arguments["balances"]:
        if (name := arguments["<account_name>"]) and not arguments["--assert"]:
            account_balance(name)
        if (name := arguments["bx ledger post <account_name>"]) and (
            amount := arguments["<amount>"]
        ):
            assert_account_balance(name, amount)
        if (is_all := arguments["--all"]) or (is_nonzero := arguments["--nonzero"]):
            balances(is_all, is_nonzero)
    elif arguments["end"]:
        end()


if __name__ == "__main__":
    main()
