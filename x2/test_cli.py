from cli import extract, Label, Offset, UserChart
from fine import T


def test_extact_label():
    assert next(extract("asset:cash")) == Label(T.Asset, "cash")


def test_extact_offset():
    assert next(extract("contra:sales:refunds")) == Offset("sales", "refunds")


def test_extact_label_multiple():
    assert list(extract("asset:cash,ap,inventory")) == [
        Label(T.Asset, "cash"),
        Label(T.Asset, "ap"),
        Label(T.Asset, "inventory"),
    ]


def test_user_chart():
    assert (
        UserChart("isa", "re", "null")
        .use(
            "asset:cash,ap,inventory,prepaid_rent",
            "capital:equity",
            "contra:equity:ts",
            "income:sales",
            "contra:sales:refunds,voids",
            "expense:salaries,rent",
        )
        .chart()
    )
