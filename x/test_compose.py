import accounts  # type: ignore
import pytest
from base import AbacusError, Entry
from compose import (  # type: ignore
    AssetLabel,
    Composer,
    ContraLabel,
    Pipeline,
    make_chart,
    Reporter,
)

# стоит разделить тесты на модульные(классы) и связные(свясь друг с другом).
# так будит удобнее понимать что вы тестируйте
# pytest.mark.parametrize("input_value", make_chart("asset:cash", "capital:equity", "contra:equity:ts"))
# def test_make_chart():
#     make = make_chart("asset:cash", "capital:equity", "contra:equity:ts")
#     # проверка равенства
#     assert make == chart0
#     # прооверка на разность ссылок
#     assert make is not chart0

# больше коминтариев в тестах. стоитиспользовать pytest.mark.


@pytest.fixture
def chart0():
    return (
        # intentionally using a mix of methods
        make_chart()
        .safe_append(AssetLabel("cash"))
        .add("capital:equity")
        .safe_append(ContraLabel(name="ts", offsets="equity"))
    )


def test_returns_offset():
    assert make_chart("asset:cash", "capital:equity", "contra:equity:ts")[
        "ts"
    ] == ContraLabel(name="ts", offsets="equity")


def test_make_chart(chart0):
    assert make_chart("asset:cash", "capital:equity", "contra:equity:ts") == chart0


def test_names(chart0):
    assert chart0.names() == [
        "current_profit",
        "retained_earnings",
        "null",
        "cash",
        "equity",
        "ts",
    ]


def test_labels(chart0):
    assert [x.name for x in chart0.labels] == [
        "cash",
        "equity",
    ]


def test_offsets(chart0):
    assert [x.name for x in chart0.contra_labels] == ["ts"]


def test_ledger_dict(chart0):
    assert chart0.ledger_dict() == {
        "cash": accounts.Asset(debits=[], credits=[]),
        "equity": accounts.Capital(debits=[], credits=[]),
        "ts": accounts.ContraCapital(debits=[], credits=[]),
        "current_profit": accounts.IncomeSummaryAccount(debits=[], credits=[]),
        "retained_earnings": accounts.RetainedEarnings(debits=[], credits=[]),
        "null": accounts.NullAccount(debits=[], credits=[]),
    }


def test_contra_pairs(chart0):
    assert chart0.contra_pairs(accounts.ContraCapital) == [ContraLabel("ts", "equity")]


def test_assets_property(chart0):
    assert chart0.assets == ["cash"]


def test_capital_property(chart0):
    assert chart0.capital == ["equity"]


def test_double_append_raises(chart0):
    with pytest.raises(AbacusError):
        chart0.add("asset:cash")


def test_double_offset_raises(chart0):
    with pytest.raises(AbacusError):
        chart0.add("contra:equity:ts")


def test_no_account_to_link_to_raises():
    with pytest.raises(AbacusError):
        make_chart().add("contra:equity:ts")


def test_as_string_and_extract():
    g = Composer()
    for string in ("expense:cogs", "contra:sales:refunds", "liability:loan"):
        assert g.as_string(g.extract(string)) == string


@pytest.fixture
def ledger0(chart0):
    chart0.add_many(["income:sales", "contra:sales:refunds", "expense:salaries"])
    ledger = chart0.ledger()
    ledger.post("cash", "equity", 12_000)
    ledger.post("ts", "cash", 2_000)
    ledger.post("cash", "sales", 3_499)
    ledger.post("refunds", "cash", 499)
    ledger.post("salaries", "cash", 2_001)
    return ledger


def test_closing_contra_entries_1(chart0, ledger0):
    assert Pipeline(chart0, ledger0).close_contra(
        accounts.ContraCapital
    ).closing_entries == [Entry(debit="equity", credit="ts", amount=2000)]


def test_closing_contra_entries_2(chart0, ledger0):
    assert Pipeline(chart0, ledger0).close_contra(
        accounts.ContraIncome
    ).closing_entries == [Entry(debit="sales", credit="refunds", amount=499)]


def test_ledger0_initial_values(ledger0):
    assert ledger0.data["salaries"].debit_and_credit() == (2001, 0)
    assert ledger0.data["sales"].debit_and_credit() == (0, 3499)
    assert ledger0.data["refunds"].debit_and_credit() == (499, 0)


def test_chaining_in_pipeline_must_not_corrupt_input_argument(chart0, ledger0):
    Pipeline(chart0, ledger0).close_first().close_second().close_last()
    assert ledger0.data["salaries"].debit_and_credit() == (2001, 0)
    assert ledger0.data["sales"].debit_and_credit() == (0, 3499)
    assert ledger0.data["refunds"].debit_and_credit() == (499, 0)


def test_balance_sheet(chart0, ledger0):
    assert Reporter(chart0, ledger0).balance_sheet().statement.dict() == {
        "assets": {"cash": 10999},
        "capital": {"equity": 10000, "retained_earnings": 999},
        "liabilities": {},
    }


def test_income_statement(chart0, ledger0):
    assert Reporter(chart0, ledger0).income_statement().statement.dict() == {
        "income": {"sales": 3000},
        "expenses": {"salaries": 2001},
    }


def test_trial_balance_view(chart0, ledger0):
    assert Reporter(chart0, ledger0).trial_balance() == {
        "cash": (10999, 0),
        "ts": (2000, 0),
        "refunds": (499, 0),
        "salaries": (2001, 0),
        "equity": (0, 12000),
        "sales": (0, 3499),
        "retained_earnings": (0, 0),
    }


def test_trial_balance_view(chart0, ledger0):
    assert isinstance(Reporter(chart0, ledger0).trial_balance().view(), str)
