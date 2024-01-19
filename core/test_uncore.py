import pytest
from uncore import ChartDict, Contra, Regular, T, regular_names, contra_names

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
        chart_dict["refunds"] = Contra("sales")


def test_invalid_contra_account_not_added_to_chart_by_method():
    with pytest.raises(KeyError):
        ChartDict().add_offset("sales", "voids")


def test_regular_names():
    chart_dict = (
        ChartDict()
        .add_regular(T.Asset, "cash")
        .add_regular(T.Capital, "equity")
        .add_offset("equity", "ts")
    )
    assert regular_names(chart_dict) == ["cash", "equity"]
    assert regular_names(chart_dict, T.Asset) == ["cash"]
    assert regular_names(chart_dict, T.Capital) == ["equity"]
    assert regular_names(chart_dict, [T.Asset, T.Capital]) == ["cash", "equity"]


def tets_contra_names():
    chart_dict = (
        ChartDict()
        .add_regular(T.Capital, "equity")
        .add_offset("equity", "ts")
    )
    assert contra_names(chart_dict) == ["ts"]
