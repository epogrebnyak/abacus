from abacus.engine.accounts import (
    Asset,
    Capital,  # type: ignore
    ContraCapital,
    IncomeSummaryAccount,
    NullAccount,
    RetainedEarnings,
)
from abacus.engine.better_chart import (
    AssetName,
    BaseChart,
    CapitalName,
    Chart,
    IncomeSummaryName,
    NullName,
    RetainedEarningsName,
)

base_chart = BaseChart(
    assets=["cash"],
    capital=["equity"],
    contra_accounts={"equity": ["ts"]},
    retained_earnings_account="re",
    income_summary_account="current_profit",
    null_account="null",
)


def test_yield_names():
    assert list(base_chart.yield_names()) == [
        AssetName(account_name="cash", contra_accounts=[]),
        CapitalName(account_name="equity", contra_accounts=["ts"]),
        RetainedEarningsName(account_name="re", contra_accounts=None),
        IncomeSummaryName(account_name="current_profit", contra_accounts=None),
        NullName(account_name="null", contra_accounts=None),
    ]


def test_ledger_items():
    assert list(base_chart.ledger_items()) == [
        ("cash", Asset),
        ("equity", Capital),
        ("ts", ContraCapital),
        ("re", RetainedEarnings),
        ("current_profit", IncomeSummaryAccount),
        ("null", NullAccount),
    ]


def test_accounts():
    assert list(CapitalName("equity", ["ts"]).accounts()) == [
        ("equity", Capital),
        ("ts", ContraCapital),
    ]


def test_filter_acocunts():
    assert list(base_chart.filter_accounts([ContraCapital])) == ["ts"]


def test_get_account():
    assert base_chart.get_label("cash") == "asset:cash"
    assert base_chart.get_label("ts") == "contra:equity:ts"


def test_chart_equiality():
    a = (
        Chart()
        .add("asset:cash")
        .name("cash", title="Cash and equivalents")
        .add("capital:equity")
        .add("contra:equity:ts", title="Treasury shares")
    )

    b = BaseChart(
        assets=["cash"],
        capital=["equity"],
        contra_accounts={"equity": ["ts"]},
    )

    c = Chart(
        base_chart=b, titles={"cash": "Cash and equivalents", "ts": "Treasury shares"}
    )
    assert a == c


def test_chaining():
    chart0 = (
        Chart()
        .add("asset:cash")
        .add("capital:equity", title="Shareholder equity")
        .add("contra:equity:ts", title="Treasury shares")
        .alias(operation="capitalize", debit="cash", credit="equity")
        .alias(operation="buyback", debit="ts", credit="cash")
        .set_isa("net_income")
        .set_re("ret")
        .set_null("nothing")
        .name("cash", "Cash and equivalents")
    )
    assert chart0


def test_chart_more_chaining():
    assert (
        Chart()
        .add("asset:cash")
        .add("capital:equity")
        .add("asset:ar", title="Accounts receivable")
        .add("asset:goods", title="Goods for resale")
        .add("expense:cogs", title="Cost of goods sold")
        .add("expense:sga", title="Selling, general and adm. expenses")
        .add("income:sales")
        .offset_many("sales", ["refunds", "voids"])
        .add("contra:equity:wd")  # fictional, may only be in partnerships
        .name("wd", title="Withdrawals")
        .offset("equity", "ts", title="Treasury shares")
        .add("liability:dd", title="Dividend due")
        .alias("invoice", debit="ar", credit="sales")
        .alias("cost", debit="goods", credit="cogs")
        .set_isa("_current_profit")
        .set_null("_null")
        .set_re("_re")
        .dict()
    ) == {
        "base_chart": {
            "assets": ["cash", "ar", "goods"],
            "expenses": ["cogs", "sga"],
            "capital": ["equity"],
            "liabilities": ["dd"],
            "income": ["sales"],
            "income_summary_account": "_current_profit",
            "retained_earnings_account": "_re",
            "contra_accounts": {"sales": ["refunds", "voids"], "equity": ["wd", "ts"]},
            "null_account": "_null",
        },
        "titles": {
            "ar": "Accounts receivable",
            "goods": "Goods for resale",
            "cogs": "Cost of goods sold",
            "sga": "Selling, general and adm. expenses",
            "wd": "Withdrawals",
            "ts": "Treasury shares",
            "dd": "Dividend due",
        },
        "operations": {"invoice": ("ar", "sales"), "cost": ("goods", "cogs")},
    }


# # ledger = chart.ledger()
# # # ledger.start() is ledger.post_compound()
# # # ledger.post_double(debit, credit, amount)
# # # ledger.post_compound(single_entries)
# # # ledger.post_alias(operations, title)
# # # ledger.close()
