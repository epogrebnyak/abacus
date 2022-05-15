from abacus.naming import variable


def test_variable():
    assert variable("Accrued interest [ai]") == ("ai", "Accrued interest")
    assert variable("[Eq]uity") == ("eq", "Equity")
    assert variable("COGS") == ("cogs", "COGS")
