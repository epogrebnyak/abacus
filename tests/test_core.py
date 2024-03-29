from copy import deepcopy

import pytest

import abacus.core as core
from abacus.core import (
    AbacusError,
    Account,
    AccountBalances,
    Asset,
    BalanceSheet,
    Capital,
    Chart,
    CompoundEntry,
    ContraIncome,
    Entry,
    IncomeStatement,
    Ledger,
    Pipeline,
    Report,
    contra_pairs,
)
from abacus.user_chart import make_user_chart


@pytest.mark.regression
def test_ledger_does_not_change_after_copy():
    le0 = (
        Chart(assets=["cash"], capital=["equity"]).ledger().post("cash", "equity", 100)
    )
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}
    le1 = deepcopy(le0)
    le1 = le1.post("cash", "equity", 200)
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}


@pytest.mark.unit
def test_contra_pairs():
    chart = Chart(
        income=[Account("sales", contra_accounts=["refunds", "voids"])],
    )
    assert contra_pairs(chart, ContraIncome) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


@pytest.mark.unit
def test_ledger_creation_with_starting_balances():
    chart = Chart(assets=["cash"], capital=["equity"])
    ledger = Ledger.new(chart, {"cash": 100, "equity": 100})
    assert ledger.balances.nonzero() == {"cash": 100, "equity": 100}


@pytest.mark.unit
def test_post_to_ledger():
    ledger = Ledger({"cash": Asset(), "equity": Capital()}).post("cash", "equity", 1000)
    assert ledger == Ledger({"cash": Asset([1000], []), "equity": Capital([], [1000])})


@pytest.mark.unit
def test_ledger_condense():
    Ledger({"cash": Asset([300, 100], [200])}).condense() == Ledger(
        {"cash": Asset([200], [])}
    )


@pytest.mark.unit
def test_ledger_fails_on_unknown_account_name():
    with pytest.raises(AbacusError):
        Ledger({"cash": Asset(), "equity": Capital()}).post("cash", "xxx", 1000)


@pytest.fixture
def chart0():
    return Chart(
        assets=["cash"],
        capital=[Account("equity", contra_accounts=["ts"])],
        income=[Account("sales", contra_accounts=["refunds", "voids"])],
        liabilities=["dividend_due"],
        expenses=["salaries"],
    )


@pytest.fixture
def entries0():
    return [
        Entry("cash", "equity", 120),
        Entry("ts", "cash", 20),
        Entry("cash", "sales", 47),
        Entry("refunds", "cash", 5),
        Entry("voids", "cash", 2),
        Entry("salaries", "cash", 30),
    ]


@pytest.mark.e2e
def test_pipleine(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    p = Pipeline(chart0, ledger).close_first().close_second().close_last()
    assert p.ledger.balances.nonzero() == {
        "cash": 110,
        "equity": 100,
        "retained_earnings": 10,
    }


@pytest.fixture
def Report0(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    return Report(chart0, ledger)


@pytest.mark.e2e
def test_balance_sheet(Report0):
    assert Report0.balance_sheet == BalanceSheet(
        assets={"cash": 110},
        capital={"equity": 100, "retained_earnings": 10},
        liabilities={"dividend_due": 0},
    )


@pytest.mark.e2e
def test_income_statement(Report0):
    assert Report0.income_statement == IncomeStatement(
        income={"sales": 40}, expenses={"salaries": 30}
    )


@pytest.mark.e2e
def test_current_profit(Report0):
    assert Report0.income_statement.current_profit() == 10


@pytest.mark.e2e
def test_trial_balance(Report0):
    assert Report0.trial_balance.data == {
        "cash": (110, 0),
        "ts": (20, 0),
        "refunds": (5, 0),
        "voids": (2, 0),
        "salaries": (30, 0),
        "equity": (0, 120),
        "retained_earnings": (0, 0),
        "dividend_due": (0, 0),
        "sales": (0, 47),
        "_isa": (0, 0),
        "_null": (0, 0),
    }


@pytest.mark.unit
def test_multiple_entry_raises():
    with pytest.raises(AbacusError):
        CompoundEntry(debits=[("cash", 10)], credits=[("eq", 18)])


@pytest.mark.unit
def test_multiple_entry_promotes():
    me = CompoundEntry(debits=[("cash", 10)], credits=[("eq", 10)])
    assert me.to_entries("null") == [Entry("cash", "null", 10), Entry("null", "eq", 10)]


@pytest.mark.unit
def test_multiple_entry_from_account_balances():
    ch = Chart(assets=["cash", "inv"], capital=[Account("eq", ["ta"])])
    ab = AccountBalances({"cash": 10, "inv": 5, "eq": 18, "ta": 3})
    assert CompoundEntry.from_balances(ch, ab) == CompoundEntry(
        debits=[("cash", 10), ("inv", 5), ("ta", 3)], credits=[("eq", 18)]
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


@pytest.fixture
def chart2():
    return make_user_chart(
        "asset:cash",
        "capital:equity",
        "contra:equity:ts",
        "income:sales",
        "contra:sales:refunds",
        "expense:salaries",
    ).chart()


def test_chart_conversion(chart2):
    assert chart2 == Chart(
        income_summary_account="_isa",
        retained_earnings_account="retained_earnings",
        null_account="_null",
        assets=[Account(name="cash", contra_accounts=[])],
        capital=[Account(name="equity", contra_accounts=["ts"])],
        liabilities=[],
        income=[Account(name="sales", contra_accounts=["refunds"])],
        expenses=[Account(name="salaries", contra_accounts=[])],
    )


@pytest.fixture
def ledger2(chart2):
    ledger = chart2.ledger()
    ledger.post("cash", "equity", 12_000)
    ledger.post("ts", "cash", 2_000)
    ledger.post("cash", "sales", 3_499)
    ledger.post("refunds", "cash", 499)
    ledger.post("salaries", "cash", 2_001)
    return ledger


def test_closing_contra_entries_1(chart2, ledger2):
    assert Pipeline(chart2, ledger2).close_contra(
        core.ContraCapital
    ).closing_entries == [Entry(debit="equity", credit="ts", amount=2000)]


def test_closing_contra_entries_2(chart2, ledger2):
    assert Pipeline(chart2, ledger2).close_contra(
        core.ContraIncome
    ).closing_entries == [Entry(debit="sales", credit="refunds", amount=499)]


def test_trial_balance_again(chart2, ledger2):
    tb = Report(chart2, ledger2).trial_balance
    assert tb["salaries"] == (2001, 0)
    assert tb["sales"] == (0, 3499)
    assert tb["refunds"] == (499, 0)


def test_chaining_in_pipeline_must_not_corrupt_input_argument(chart2, ledger2):
    Pipeline(chart2, ledger2).close_first().close_second().close_last()
    assert ledger2["salaries"].balance() == 2001
    assert ledger2["sales"].balance() == 3499
    assert ledger2["refunds"].balance() == 499


def test_balance_sheet_again(chart2, ledger2):
    assert Report(chart2, ledger2).balance_sheet == BalanceSheet(
        assets={"cash": 10999},
        capital={"equity": 10000, "retained_earnings": 999},
        liabilities={},
    )


def test_income_statement_again(chart2, ledger2):
    assert Report(chart2, ledger2).income_statement == IncomeStatement(
        income={"sales": 3000},
        expenses={"salaries": 2001},
    )


def test_trial_balance_view(chart2, ledger2):
    assert Report(chart2, ledger2).trial_balance == {
        "cash": (10999, 0),
        "ts": (2000, 0),
        "refunds": (499, 0),
        "salaries": (2001, 0),
        "equity": (0, 12000),
        "sales": (0, 3499),
        "retained_earnings": (0, 0),
        "_isa": (0, 0),
        "_null": (0, 0),
    }


def test_serialisation():
    e = Entry("a", "b", 1)
    assert e.from_string(e.to_json()) == e
    assert e.to_json() == '{"debit": "a", "credit": "b", "amount": 1}'


def test_print_all():
    chart = Chart(
        assets=["cash"],
        capital=["equity"],
        income=["services"],
        expenses=["marketing", "salaries"],
    )

    # Create a ledger using the chart
    ledger = chart.ledger()

    # Post entries to ledger
    ledger.post(debit="cash", credit="equity", amount=5000)
    ledger.post(debit="marketing", credit="cash", amount=1000)
    ledger.post(debit="cash", credit="services", amount=3499)
    ledger.post(debit="salaries", credit="cash", amount=2000)

    # Print trial balance, balance sheet and income statement
    report = Report(chart, ledger).rename("re", "Retained earnings")
    assert report.print_all() is None
