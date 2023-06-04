from abacus.accounts import ContraAsset
from abacus.journal import Journal
from abacus.ledger import OpenContraAccount


def test_open_contra():
    j = Journal()
    oe = OpenContraAccount("depreciation", "ContraAsset", 0, "ppe")
    assert j.post_many([oe]).ledger() == {
        "depreciation": ContraAsset(link="ppe", debits=[], credits=[0])
    }
