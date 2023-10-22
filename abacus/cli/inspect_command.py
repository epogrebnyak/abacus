import sys

from abacus import Amount
from abacus.engine.accounts import CreditAccount, DebitAccount


def side(ledger, account_name):
    match ledger[account_name]:
        case DebitAccount(_, _):
            return "debit"
        case CreditAccount(_, _):
            return "credit"
        case _:
            raise TypeError(ledger[account_name].__class__.__name__)


def print_account_info(ledger, chart, account_name: str):
    account = ledger[account_name]
    print("     Account:", chart.namer[account_name])
    print("  Short name:", account_name)
    print("   Long name:", chart.namer.compose_name_long(account_name))
    print("        Code:", chart.codes.get(account_name, "not assigned"))
    print("        Type:", account.split_on_caps())
    print("      Debits:", str(account.debits) + ",", "total", sum(account.debits))
    print("     Credits:", str(account.credits) + ",", "total", sum(account.credits))
    print("     Balance:", account.balance())
    print("Balance side:", side(ledger, account_name).capitalize())


def assert_account_balance(ledger, account_name: str, assert_amount: Amount):
    amount = ledger[account_name].balance()
    expected_amount = Amount(assert_amount)
    msg_ok = f"Check passed for account {account_name}, account balance is {expected_amount} as expected."
    msg_fail = f"Check failed for {account_name}, expected balance is {expected_amount}, got {amount}."
    if amount != expected_amount:
        sys.exit(msg_fail)
    print(msg_ok)
