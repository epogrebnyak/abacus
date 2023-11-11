from abacus.engine.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraCapital,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    NullAccount,
    RetainedEarnings,
)
from abacus.engine.base import Entry, MultipleEntry
from abacus.engine.better_chart import BaseChart, Chart
from abacus.engine.ledger import Ledger, to_multiple_entry, unsafe_post_entries


def test_ledger(ledger):
    assert {
        k: v
        for k, v in ledger.subset([Asset, Expense, ContraIncome])
        .deep_copy()
        .condense()
        .balances()
        .items()
        if v
    } == {"cash": 1000, "ar": 200, "refunds": 50}


def test_ledger_new():
    assert Chart().asset("cash").capital("equity").ledger().data == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "null": NullAccount(debits=[], credits=[]),
    }


def test_ledger_post():
    ledger1 = Chart().asset("cash").capital("equity").ledger()
    ledger1.post(Entry(debit="cash", credit="equity", amount=799))
    ledger1.post(Entry(debit="cash", credit="equity", amount=201))
    assert ledger1["cash"].debits == ledger1["equity"].credits == [799, 201]
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000


def test_ledger_deep_copy():
    ledger1 = Chart().asset("cash").capital("equity").ledger()
    ledger1.post(Entry(debit="cash", credit="equity", amount=799))
    ledger1.post(Entry(debit="cash", credit="equity", amount=201))
    ledger2 = ledger1.deep_copy()
    ledger2.post(Entry(debit="cash", credit="equity", amount=-1000))
    # ledger1 not affected
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000
    # ledger2 changed
    assert ledger2["cash"].balance() == ledger2["equity"].balance() == 0


def test_ledger_report_balance_sheet(chart, ledger):
    assert ledger.balance_sheet(chart).dict() == {
        "assets": {"cash": 1000, "ar": 200, "goods": 0},
        "capital": {"equity": 1000, "re": 200},
        "liabilities": {},
    }


def test_ledger_report_income_statement(chart, ledger):
    assert ledger.income_statement(chart).dict() == {
        "income": {"sales": 200},
        "expenses": {"cogs": 0, "sga": 0},
    }


def test_journal_with_starting_balance():
    chart = Chart(
        base_chart=BaseChart(
            assets=["cash"],
            capital=["equity"],
            expenses=["salaries", "rent"],
            liabilities=[],
            income=["services"],
        )
    )
    ledger = chart.ledger()

    # Account balances are known from previous period end
    starting_balances = {"cash": 1400, "equity": 1500, "re": -100}
    assert to_multiple_entry(ledger, starting_balances) == MultipleEntry(
        [("cash", 1400)],
        [("equity", 1500), ("re", -100)],
    )


def test_post_many():
    chart = Chart(
        base_chart=BaseChart(
            assets=["cash", "goods_for_sale"],
            expenses=["cogs", "sga"],
            capital=["equity"],
            income=["sales"],
            liabilities=[],
        )
    ).offset_many("sales", ["discounts", "cashback"])

    starting_balances = {"cash": 10, "goods_for_sale": 10, "equity": 20}
    ledger = chart.ledger(starting_balances)
    e1 = Entry(debit="cash", credit="equity", amount=1000)  # pay in capital
    e2 = Entry(
        debit="goods_for_sale", credit="cash", amount=250
    )  # acquire goods worth 250
    e3 = Entry(
        credit="goods_for_sale", debit="cogs", amount=200
    )  # sell goods worth 200
    e4 = Entry(credit="sales", debit="cash", amount=400)  # for 400 in cash
    e5 = Entry(credit="cash", debit="sga", amount=50)  # administrative expenses
    ledger.post_many([e1, e2, e3, e4, e5])
    assert ledger.income_statement(chart).current_profit() == 150


def test_make_ledger():
    chart = Chart().asset("cash").capital("equity")
    assert chart.ledger() == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "null": NullAccount(debits=[], credits=[]),
    }


def test_unsafe_process_entries():
    _ledger = Ledger(
        {
            "cash": Asset(debits=[], credits=[]),
            "equity": Capital(debits=[], credits=[]),
        }
    )
    _, failed = unsafe_post_entries(_ledger, [Entry("", "", 0)])
    assert failed == [Entry("", "", 0)]


def test_create_ledger_again():
    (
        Chart(
            base_chart=BaseChart(
                assets=["cash", "goods", "ppe"],
                capital=["equity", "re"],
                income=["sales"],
                expenses=["cogs", "sga"],
            )
        )
        .offset("ppe", "depreciation")
        # https://stripe.com/docs/revenue-recognition/methodology
        .offset_many("sales", ["refunds", "voids"])
        .ledger()
    ) == {
        "cash": Asset(debits=[], credits=[]),
        "goods": Asset(debits=[], credits=[]),
        "ppe": Asset(debits=[], credits=[]),
        "cogs": Expense(debits=[], credits=[]),
        "sga": Expense(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "refunds": ContraIncome(debits=[], credits=[]),
        "voids": ContraIncome(debits=[], credits=[]),
        "null": NullAccount(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
    }


def test_make_ledger_with_netting():
    chart = Chart().asset("ppe").capital("shares").income("sales")
    chart.base_chart.contra_accounts = {
        "sales": ["refunds", "voids"],
        "shares": ["treasury_shares"],
        "ppe": ["depreciation"],
    }
    assert chart.ledger() == {
        "ppe": Asset(
            debits=[],
            credits=[],
        ),
        "shares": Capital(
            debits=[],
            credits=[],
        ),
        "re": RetainedEarnings(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "refunds": ContraIncome(debits=[], credits=[]),
        "voids": ContraIncome(debits=[], credits=[]),
        "treasury_shares": ContraCapital(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "null": NullAccount(debits=[], credits=[]),
    }
