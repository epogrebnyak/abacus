import pytest
import uncore
from uncore import (
    Account,
    BalanceSheet,
    Chart,
    ChartDict,
    Contra,
    IncomeStatement,
    Intermediate,
    Journal,
    Move,
    Pipeline,
    Regular,
    Side,
    T,
    close,
    credit,
    debit,
    double_entry,
)


def test_contra_account_added_to_chart():
    chart_dict = ChartDict().add(T.Income, "sales").offset("sales", "refunds")
    assert chart_dict["sales"] == Regular(T.Income)
    assert chart_dict["refunds"] == Contra(T.Income)


def test_invalid_contra_account_not_added_to_chart_by_method():
    with pytest.raises(KeyError):
        ChartDict().offset("sales", "voids")


def test_chart_regular_names():
    chart_dict = (
        ChartDict().add(T.Asset, "cash").add(T.Capital, "equity").offset("equity", "ts")
    )
    assert chart_dict.regular_names(T.Asset) == ["cash"]
    assert chart_dict.regular_names(T.Capital) == ["equity"]
    assert chart_dict.regular_names(T.Asset, T.Capital) == ["cash", "equity"]


def test_chart_dict_contra_pairs():
    chart_dict = ChartDict().add(T.Capital, "equity").offset("equity", "ts")
    assert chart_dict.contra_pairs(T.Capital) == [("equity", "ts")]


def test_chart_contra_pairs():
    assert Chart("isa", "re").add(
        T.Income, "sales", contra_names=["refunds", "voids"]
    ).dict.contra_pairs(T.Income) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


def test_chart_creation():
    chart0 = (
        Chart(
            income_summary_account="income_summary_account",
            retained_earnings_account="retained_earnings",
        )
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Asset, "cash")
        .add(T.Capital, "equity", contra_names=["buyback"])
    )
    assert chart0.dict == ChartDict(
        {
            "cash": T.Asset,
            "sales": T.Income,
            "equity": T.Capital,
        },
        {
            "refunds": "sales",
            "voids": "sales",
            "buyback": "equity",
        },
    )
    assert chart0.retained_earnings_account == "retained_earnings"
    assert chart0.income_summary_account == "income_summary_account"


def test_journal_creation():
    j = Journal.new(ChartDict().add(T.Asset, "cash").offset("cash", "contra_cash"))
    assert j.set_isa("isa").set_re("re") == Journal(
        {
            "cash": Account(Regular(T.Asset)),
            "contra_cash": Account(Contra(T.Asset)),
            "re": Account(Regular(T.Capital)),
            "isa": Account(Intermediate(Side.Credit)),
        }
    )


@pytest.fixture
def chart():
    return (
        Chart(
            retained_earnings_account="retained_earnings",
            income_summary_account="income_summary_account",
        )
        .add_many(T.Asset, "cash", "ar")
        .add(T.Capital, "equity", contra_names=["buyback"])
        .add(T.Income, "sales", contra_names=["refunds", "voids"])
        .add(T.Liability, "vat")
        .add(T.Expense, "salary")
    )


@pytest.fixture
def journal(chart):
    j = Journal.from_chart(chart)
    j.post_many(
        [
            double_entry("cash", "equity", 1200),
            double_entry("buyback", "cash", 200),
            [debit("ar", 70), credit("sales", 60), credit("vat", 10)],
            double_entry("cash", "ar", 30),
            [
                debit("voids", 20),
                debit("refunds", 10),
                debit("vat", 5),
                credit("ar", 35),
            ],
            [debit("salary", 18), credit("cash", 18)],
        ]
    )
    return j


def test_journal_has_retained_earnings(chart):
    j = Journal.from_chart(chart)
    assert j[chart.retained_earnings_account].flavor == Regular(T.Capital)


def test_balances(journal):
    assert journal.balances == {
        "cash": 1012,
        "ar": 5,
        "equity": 1200,
        "buyback": 200,
        "sales": 60,
        "refunds": 10,
        "voids": 20,
        "vat": 5,
        "salary": 18,
        "retained_earnings": 0,
        "income_summary_account": 0,
    }


def test_tuples(journal):
    assert journal.tuples == {
        "cash": (1230, 218),
        "ar": (70, 65),
        "equity": (0, 1200),
        "buyback": (200, 0),
        "sales": (0, 60),
        "refunds": (10, 0),
        "voids": (20, 0),
        "vat": (5, 10),
        "salary": (18, 0),
        "retained_earnings": (0, 0),
        "income_summary_account": (0, 0),
    }


def test_subset(journal):
    assert journal.subset(T.Asset).balances == {"cash": 1012, "ar": 5}


@pytest.fixture
def pipeline(chart, journal):
    return Pipeline(chart, journal)


def test_moves_income(pipeline):
    assert pipeline.close_contra(T.Income).moves == [
        Move(frm="refunds", to="sales"),
        Move(frm="voids", to="sales"),
    ]


def test_moves_capital(pipeline):
    assert pipeline.close_contra(T.Capital).moves == [Move(frm="buyback", to="equity")]


def test_moves_close_temp(pipeline):
    assert pipeline.close_contra(
        T.Income, T.Expense
    ).flush().close_temporary().moves == [
        Move(frm="sales", to="income_summary_account"),
        Move(frm="salary", to="income_summary_account"),
    ]


def test_equate_close_isa_entry(pipeline, chart):
    p = pipeline.close_contra(T.Income, T.Expense).close_temporary()
    a = p.flush().close_isa().closing_entries
    b = [
        double_entry(
            chart.income_summary_account,
            chart.retained_earnings_account,
            12,
        )
    ]
    assert a == b


def test_ledger_does_not_change_after_pipeline_application(chart, journal):
    assert journal.balances["retained_earnings"] == 0
    assert close(chart, journal).balances["retained_earnings"] == 12
    assert journal.balances["retained_earnings"] == 0
    assert journal.tuples["retained_earnings"] == (0, 0)


def test_equity_nets_out_to_1000(chart, journal):
    assert close(chart, journal).balances["equity"] == 1000


def test_close_pipeline_logic(chart, journal):
    assert close(chart, journal) == (
        Pipeline(chart, journal)
        .close_contra(T.Income, T.Expense)
        .close_temporary()
        .close_isa()
        .close_contra(T.Asset, T.Capital, T.Liability)
        .journal
    )


@pytest.fixture
def income_statement(chart, journal):
    return uncore.income_statement(chart, journal)


@pytest.fixture
def balance_sheet(chart, journal):
    return uncore.balance_sheet(chart, journal)


def test_statements(chart, journal, income_statement, balance_sheet):
    _, i, b, _ = uncore.statements(chart, journal)
    assert i == income_statement
    assert b == balance_sheet


def test_income_statement(income_statement):
    assert income_statement == IncomeStatement(
        income={"sales": 30}, expenses={"salary": 18}
    )


def test_balance_sheet(balance_sheet):
    assert balance_sheet == BalanceSheet(
        assets={"cash": 1012, "ar": 5},
        capital={"equity": 1000, "retained_earnings": 12},
        liabilities={"vat": 5},
    )


def test_current_profit(income_statement):
    assert income_statement.current_profit == 12
