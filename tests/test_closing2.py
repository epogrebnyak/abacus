from abacus.accounts import ContraIncome, Income
from abacus.closing import close_contra_accounts
from abacus.closing_types import CloseContraIncome
from abacus.ledger import Ledger


def test_transfer_entry():
    assert ContraIncome([8], []).balance() == 8


def test_close_contra_accounts_with_netting():
    ledger = Ledger({"sales": Income([], [200]), "discounts": ContraIncome([8], [])})
    netting = {"sales": ["discounts"]}
    assert close_contra_accounts(ledger, netting, Income) == [
        CloseContraIncome("sales", "discounts", 8)
    ]
