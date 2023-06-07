from abacus.accounts import ContraAsset, OpenContraAccount


def test_open_contra():
    oe = OpenContraAccount("depreciation", "ContraAsset", "ppe")
    assert oe.new() == ContraAsset(link="ppe", debits=[], credits=[])
