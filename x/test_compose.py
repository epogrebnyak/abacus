import pytest
from base import AbacusError, Entry
from compose import (  # type: ignore
    AssetLabel,
    CapitalLabel,
    ChartList,
    Composer,
    IncomeSummaryLabel,
    NullLabel,
    Offset,
    RetainedEarningsLabel,
    base_chart_list,
    make_chart,
    closing_contra_entries,
    chain,
    close_first,
    close_second,
    close_last,
)

import accounts  # type: ignore


@pytest.fixture
def chart_list():
    return (
        base_chart_list()
        .safe_append(AssetLabel("cash"))
        .add("capital:equity")
        .safe_append(Offset(name="ts", offsets="equity"))
    )


def test_returns_offset():
    assert ChartList([CapitalLabel("equity"), Offset("ts", "equity")])["ts"] == Offset(
        name="ts", offsets="equity"
    )


def test_make_chart(chart_list):
    assert make_chart("asset:cash", "capital:equity", "contra:equity:ts") == chart_list


def test_names(chart_list):
    assert chart_list.names() == [
        "current_profit",
        "retained_earnings",
        "null",
        "cash",
        "equity",
        "ts",
    ]


def test_labels(chart_list):
    assert [x.name for x in chart_list.labels] == [
        "current_profit",
        "retained_earnings",
        "null",
        "cash",
        "equity",
    ]


def test_offsets(chart_list):
    assert [x.name for x in chart_list.offsets] == ["ts"]


def test_ledger_dict(chart_list):
    assert chart_list.ledger_dict() == {
        "cash": accounts.Asset(debits=[], credits=[]),
        "equity": accounts.Capital(debits=[], credits=[]),
        "ts": accounts.ContraCapital(debits=[], credits=[]),
        "current_profit": accounts.IncomeSummaryAccount(debits=[], credits=[]),
        "retained_earnings": accounts.RetainedEarnings(debits=[], credits=[]),
        "null": accounts.NullAccount(debits=[], credits=[]),
    }


def test_contra_pairs(chart_list):
    assert chart_list.contra_pairs(accounts.ContraCapital) == [Offset("ts", "equity")]


def test_assets_property(chart_list):
    assert chart_list.assets == ["cash"]


def test_capital_property(chart_list):
    assert chart_list.capital == ["equity"]


def test_double_append_raises(chart_list):
    with pytest.raises(AbacusError):
        chart_list.add("asset:cash")


def test_double_offset_raises(chart_list):
    with pytest.raises(AbacusError):
        chart_list.add("contra:equity:ts")


def test_no_account_to_link_to_raises(chart_list):
    with pytest.raises(AbacusError):
        ChartList(accounts=[]).add("contra:equity:ts")


def test_as_string_and_extract():
    g = Composer()
    for string in ("expense:cogs", "contra:sales:refunds", "liability:loan"):
        assert g.as_string(g.extract(string)) == string


@pytest.fixture
def ledger0(chart_list):
    chart_list.add_many("income:sales", "contra:sales:refunds", "expense:salaries")
    ledger = chart_list.ledger()
    ledger.post("cash", "equity", 12_000)
    ledger.post("ts", "cash", 2_000)
    ledger.post("cash", "sales", 3_499)
    ledger.post("refunds", "cash", 499)
    ledger.post("salaries", "cash", 2_001)
    return ledger


def test_closing_contra_entries_1(chart_list, ledger0):
    es1 = list(closing_contra_entries(chart_list, ledger0, accounts.ContraCapital))
    assert es1 == [Entry(debit="equity", credit="ts", amount=2000)]


def test_closing_contra_entries_2(chart_list, ledger0):
    es2 = list(closing_contra_entries(chart_list, ledger0, accounts.ContraIncome))
    assert es2 == [Entry(debit="sales", credit="refunds", amount=499)]


def test_ledger0_initial_values(ledger0):
    assert ledger0.data["salaries"].debit_and_credit() == (2001, 0)
    assert ledger0.data["sales"].debit_and_credit() == (0, 3499)
    assert ledger0.data["refunds"].debit_and_credit() == (499, 0)


def test_chain_must_not_corrupt_the_argument(chart_list, ledger0):
    _, _ = chain(
        chart_list, ledger0, [close_first, close_second, close_last]
    )
    assert ledger0.data["salaries"].debit_and_credit() == (2001, 0)
    assert ledger0.data["sales"].debit_and_credit() == (0, 3499)
    assert ledger0.data["refunds"].debit_and_credit() == (499, 0)
