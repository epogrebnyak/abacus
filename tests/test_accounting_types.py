from abacus.accounting_types import AccountBalancesDict


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
