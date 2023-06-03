from abacus import Entry, Ledger, Pipeline
from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
)

ledger = Ledger(
    {
        "cash": Asset(debits=[], credits=[]),
        "goods_for_sale": Asset(debits=[], credits=[]),
        "ppe": Asset(debits=[], credits=[]),
        "cogs": Expense(debits=[], credits=[]),
        "sga": Expense(debits=[], credits=[]),
        "depreciation_expense": Expense(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "re": Capital(debits=[], credits=[]),
        "divp": Liability(debits=[], credits=[]),
        "sales": Income(debits=[], credits=[]),
        "depreciation": ContraAsset(debits=[], credits=[], link="ppe"),
        "discount": ContraIncome(debits=[], credits=[], link="sales"),
        "returns": ContraIncome(debits=[], credits=[], link="sales"),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
)


def test_pipeline():
    pipeline = Pipeline(ledger)
    pipeline.add_entry("cash", "equity", 3000)
    pipeline.add_entry("ppe", "cash", 2000)
    pipeline.add_entries(
        [
            Entry("depreciation_expense", "depreciation", 200),
            Entry("depreciation_expense", "depreciation", 200),
        ]
    )
    assert pipeline.postings == [
        Entry(dr="cash", cr="equity", amount=3000),
        Entry(dr="ppe", cr="cash", amount=2000),
        Entry(dr="depreciation_expense", cr="depreciation", amount=200),
        Entry(dr="depreciation_expense", cr="depreciation", amount=200),
    ]


def test_pipeline_run():
    pipeline = Pipeline(
        ledger,
        postings=[
            Entry(dr="cash", cr="equity", amount=3000),
            Entry(dr="ppe", cr="cash", amount=2000),
            Entry(dr="depreciation_expense", cr="depreciation", amount=200),
            Entry(dr="depreciation_expense", cr="depreciation", amount=200),
        ],
    )
    assert pipeline.run().balances() == {
        "cash": 1000,
        "goods_for_sale": 0,
        "ppe": 2000,
        "cogs": 0,
        "sga": 0,
        "depreciation_expense": 400,
        "equity": 3000,
        "re": 0,
        "divp": 0,
        "sales": 0,
        "depreciation": 400,
        "discount": 0,
        "returns": 0,
        "profit": 0,
    }
