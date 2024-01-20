import pytest
from uncore import ChartDict, Chart, Contra, Regular, T, Asset

# test case: overwrite any reserved name in Chart


def test_contra_account_added_to_chart():
    chart_dict = (
        ChartDict().add_regular(T.Income, "sales").add_offset("sales", "refunds")
    )
    assert chart_dict["sales"] == Regular(T.Income)
    assert chart_dict["refunds"] == Contra("sales")


def test_invalid_contra_account_not_added_to_chart_by_assignment():
    chart_dict = ChartDict()
    with pytest.raises(KeyError):
        chart_dict["voids"] = Contra("sales")


def test_invalid_contra_account_not_added_to_chart_by_method():
    with pytest.raises(KeyError):
        ChartDict().add_offset("sales", "voids")


def test_chart_regular_names():
    chart_dict = (
        ChartDict()
        .add_regular(T.Asset, "cash")
        .add_regular(T.Capital, "equity")
        .add_offset("equity", "ts")
    )
    assert chart_dict.regular_names([T.Asset]) == ["cash"]
    assert chart_dict.regular_names([T.Capital]) == ["equity"]
    assert chart_dict.regular_names([T.Asset, T.Capital]) == ["cash", "equity"]


def test_chart_dict_contra_pairs():
    chart_dict = ChartDict().add_regular(T.Capital, "equity").add_offset("equity", "ts")
    assert chart_dict.contra_pairs(T.Capital) == [("equity", "ts")]


def test_chart_contra_pairs():
    chart = (
        Chart()
        .add(T.Capital, "equity", contra_names=["buyback"])
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
    )
    assert chart.dict.contra_pairs(T.Income) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]
    assert chart.dict.contra_pairs(T.Capital) == [("equity", "buyback")]


def test_chart_creation():
    chart0 = (
        Chart()
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Asset, "cash")
        .add(T.Capital, "equity", contra_names=["buyback"])
    )
    chart_dict0 = ChartDict(
        {
            "cash": Regular(t=T.Asset),
            "sales": Regular(t=T.Income),
            "refunds": Contra(links_to="sales"),
            "voids": Contra(links_to="sales"),
            "equity": Regular(t=T.Capital),
            "buyback": Contra(links_to="equity"),
        }
    )
    assert chart0.dict == chart_dict0
    assert chart0.retained_earnings_account == "retained_earnings"
    assert chart0.income_summary_account == "income_summary_account"


def test_condense():
    assert Asset([10, 20], [5]).condense() == Asset([25], [])
