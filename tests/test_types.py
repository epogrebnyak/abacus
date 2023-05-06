from abacus.accounting_types import AccountBalancesDict, CreditAccount, DebitAccount


def test_debit_credit():
    da = DebitAccount([], [])
    da.debit(10)
    da.credit(2)
    assert da == DebitAccount(debits=[10], credits=[2])


def test_account_safe_copy():
    da = DebitAccount(debits=[10], credits=[2])
    da2 = da.safe_copy()
    da2.debit(8)
    da2.credit(15)
    assert da2 == DebitAccount(debits=[10, 8], credits=[2, 15])
    assert da == DebitAccount(debits=[10], credits=[2])


def test_balance_on_DebitAccount():
    assert DebitAccount([10, 10], [5]).balance() == 10 + 10 - 5


def test_balance_on_CreditAccount():
    assert CreditAccount([2, 2], [5, 4]).balance() == 5 + 4 - 2 - 2


def test_AccountBalanceDict():
    assert (
        AccountBalancesDict(
            [
                ("a", 3),
                ("b", -1),
            ]
        ).total()
        == 2
    )
