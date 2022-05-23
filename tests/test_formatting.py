from abacus.formatting import Line, println, side_by_side, to_strings


def test_formatting():
    lines = Line("Cash", 500), Line("Accounts Receivable", 100_500)
    assert to_strings(lines) == [
        "  Cash..................    500",
        "  Accounts receivable... 100500",
    ]

    lines2 = [Line("Equity", 100_000), Line("Profit", 1000)]
    assert to_strings(lines2) == ["  Equity... 100000", "  Profit...   1000"]

    assert side_by_side(
        ["Assets"] + to_strings(lines), ["Capital"] + to_strings(lines2)
    ) == [
        "Assets                          Capital",
        "  Cash..................    500   Equity... 100000",
        "  Accounts receivable... 100500   Profit...   1000",
    ]
