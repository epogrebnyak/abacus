from abacus.engine.accounts import (
    Asset,
    AssetName,
    ContraIncome,
    ContraName,
    CreditAccount,
    DebitAccount,
    extract,
)


def test_asset_topup():
    assert Asset([10], []).topup(10) == Asset([10, 10], [])


def test_asset_condense():
    assert Asset([10, 10], []).condense() == Asset([20], [])


def test_split_on_caps():
    assert DebitAccount([], []).split_on_caps() == "Debit Account"


def test_debit_credit():
    da = DebitAccount([], [])
    da.debit(10)
    da.credit(2)
    assert da == DebitAccount(debits=[10], credits=[2])


def test_account_safe_copy():
    da = DebitAccount(debits=[10], credits=[2])
    da2 = da.deep_copy()
    da2.debit(8)
    da2.credit(15)
    assert da2 == DebitAccount(debits=[10, 8], credits=[2, 15])
    assert da == DebitAccount(debits=[10], credits=[2])


def test_balance_on_DebitAccount():
    assert DebitAccount([10, 10], [5]).balance() == 10 + 10 - 5


def test_balance_on_CreditAccount():
    assert CreditAccount([2, 2], [5, 4]).balance() == 5 + 4 - 2 - 2


def test_ContraIncome():
    assert ContraIncome([8], []).balance() == 8


def test_extract():
    assert extract("contra:sales:voids") == ContraName("sales", "voids")
    assert extract("asset:cash") == AssetName("cash")
