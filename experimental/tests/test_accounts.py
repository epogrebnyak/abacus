from engine.accounts import Asset


def test_asset_topup():
    assert Asset([10], []).topup(10) == Asset([10, 10], [])


def test_asset_condense():
    assert Asset([10, 10], []).condense() == Asset([20], [])
