import pytest
from composer import ChartList, CapitalLabel, RetainedEarningsLabel, NullLabel, IncomeSummaryLabel, AssetLabel, Chart, Composer, Offset, base, base_chart_list, create_chart  # type: ignore

import abacus.engine.accounts as accounts  # type: ignore


@pytest.fixture
def chart_list():
    return (
        base_chart_list()
        .safe_append(AssetLabel("cash"))
        .add("capital:equity")
        .safe_append(Offset("equity", "ts"))
    )


def test_to_base_chart():
    bc = base()
    bc.assets = ["cash"]
    bc.capital = ["equity"]
    assert bc.to_chart_list() == ChartList(
        accounts=[
            IncomeSummaryLabel(name="current_profit"),
            RetainedEarningsLabel(name="retained_earnings"),
            NullLabel(name="null"),
            AssetLabel(name="cash"),
            CapitalLabel(name="equity"),
            Offset(name="equity", contra="ts"),
        ]
    )


#
# [('cash', <class 'abacus.engine.accounts.Asset'>), ('equity', <class 'abacus.engine.accounts.Capital'>), ('ts', <class 'abacus.engine.accounts.ContraCapital'>), ('current_profit', <class 'abacus.engine.accounts.IncomeSummaryAccount'>), ('retained_earnings', <class 'abacus.engine.accounts.RetainedEarnings'>), ('null', <class 'abacus.engine.accounts.NullAccount'>)]
#
# [('equity', 'ts')]
# ['cash']
# ['equity']
# income_summary_account='current_profit' retained_earnings_account='retained_earnings' null_account='null' assets=['cash'] expenses=[] capital=['equity'] liabilities=[] income=[] contra_accounts={'equity': ['ts']}


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
    assert chart_list.contra_pairs(accounts.ContraCapital) == [("equity", "ts")]


def test_assets_property(chart_list):
    assert chart_list.assets == ["cash"]


def test_capital_property(chart_list):
    assert chart_list.capital == ["equity"]


def test_to_base_chart(chart_list):
    assert chart_list.to_base_chart()


def test_double_append_raises(chart_list):
    with pytest.raises(ValueError):
        chart_list.add("asset:cash")


def test_double_offset_raises(chart_list):
    with pytest.raises(ValueError):
        chart_list.add("contra:equity:ts")


def test_make_chart_runs():
    assert create_chart(
        assets=["cash"],
        capital=["equity"],
        income=["services"],
        expenses=["marketing", "salaries"],
    )


def test_as_string_and_extract():
    g = Composer()
    for string in ("expense:cogs", "contra:sales:refunds", "liability:loan"):
        assert g.as_string(g.extract(string)) == string


def test_base():
    assert base().dict() == {
        "income_summary_account": "current_profit",
        "retained_earnings_account": "retained_earnings",
        "null_account": "null",
        "assets": [],
        "expenses": [],
        "capital": [],
        "liabilities": [],
        "income": [],
        "contra_accounts": {},
    }


def test_contra_accounts():
    b = (
        base()
        .add("income:sales")
        .add("contra:sales:refunds")
        .promote(Offset("sales", "voids"))
    )
    assert b.contra_accounts == {"sales": ["refunds", "voids"]}


@pytest.fixture
def chart0():
    return (
        Chart()
        .add("asset:cash")
        .add("capital:equity")
        .add_many(["cogs", "sga"], prefix="expense")
        .name("cogs", "Cost of goods sold")
        .name("sga", "Selling, general, and adm. expenses")
        .add("contra:equity:ts")
        .name("ts", "Treasury share")
        .add("income:sales")
        .add_many(["refunds", "voids"], prefix="contra:sales")
        .add("asset:ar")
        .alias("invoice", "ar", "sales")
        .alias("accept", "cash", "ar")
        .add("asset:inventory")
        .alias("cost", "cogs", "inventory")
        .alias("purchase", "inventory", "cash")
        .alias("refund", "refunds", "cash")
        .add_many(["dd", "ap"], prefix="liability")
    )


def test_operations(chart0):
    assert chart0.operations == {
        "invoice": ("ar", "sales"),
        "accept": ("cash", "ar"),
        "cost": ("cogs", "inventory"),
        "purchase": ("inventory", "cash"),
        "refund": ("refunds", "cash"),
    }


def test_composer(chart0):
    assert chart0.composer.as_string(AssetLabel("cash")) == "asset:cash"


def test_dict(chart0):
    assert chart0.dict() == {
        "base": {
            "income_summary_account": "current_profit",
            "retained_earnings_account": "retained_earnings",
            "null_account": "null",
            "assets": ["cash", "ar", "inventory"],
            "expenses": ["cogs", "sga"],
            "capital": ["equity"],
            "liabilities": ["dd", "ap"],
            "income": ["sales"],
            "contra_accounts": {"equity": ["ts"], "sales": ["refunds", "voids"]},
        },
        "titles": {
            "cogs": "Cost of goods sold",
            "sga": "Selling, general, and adm. expenses",
            "ts": "Treasury share",
        },
        "operations": {
            "invoice": ("ar", "sales"),
            "accept": ("cash", "ar"),
            "cost": ("cogs", "inventory"),
            "purchase": ("inventory", "cash"),
            "refund": ("refunds", "cash"),
        },
        "composer": {
            "asset": "asset",
            "capital": "capital",
            "liability": "liability",
            "income": "income",
            "expense": "expense",
            "contra": "contra",
            "income_summary": "isa",
            "retained_earnings": "re",
            "null": "null",
        },
    }


def test_ledger_keys(chart0):
    assert list(chart0.ledger().data.keys()) == [
        "cash",
        "ar",
        "inventory",
        "equity",
        "ts",
        "dd",
        "ap",
        "sales",
        "refunds",
        "voids",
        "cogs",
        "sga",
        "current_profit",
        "retained_earnings",
        "null",
    ]


def test_ledger_creation(chart0):
    from ledger import Ledger

    assert isinstance(chart0.ledger(), Ledger)


def test_ledger_component(chart0):
    assert chart0.ledger().data["cash"] == accounts.Asset(debits=[], credits=[])


def test_contra_pairs(chart0):
    assert chart0.base.contra_pairs(accounts.ContraIncome) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


def test_label_permanent(chart0):
    assert str(chart0.label("sales")) == "income:sales"


def test_label_contra(chart0):
    assert str(chart0.label("refunds")) == "contra:sales:refunds"
