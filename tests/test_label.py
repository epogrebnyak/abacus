from abacus.engine.better_chart import BaseChart
from abacus.engine.label_layer import (
    ContraLabel,
    Prefix,
    RegularLabel,
    Unique,
    UniqueLabel,
    extract,
    to_chart,
)


def test_extract_on_re():
    assert extract("re:retained_earnings") == UniqueLabel(
        Unique.RE, "retained_earnings"
    )


def test_extract():
    assert extract("asset:cash") == RegularLabel(Prefix.ASSET, "cash")
    assert extract("contra:sales:refunds") == ContraLabel("sales", "refunds")


def test_label_string():
    assert str(RegularLabel(Prefix.ASSET, "cash")) == "asset:cash"
    assert str(ContraLabel("sales", "refunds")) == "contra:sales:refunds"


def test_to_chart():
    assert to_chart(
        [
            "asset:cash",
            "capital:equity",
            "contra:equity:ts",
            "re:retained_earnings",
            "null:null",
            "isa:current_profit",
        ]
    ) == BaseChart(
        assets=["cash"],
        capital=["equity"],
        contra_accounts={"equity": ["ts"]},
        retained_earnings_account="retained_earnings",
        null_account="null",
        income_summary_account="current_profit",
    )
