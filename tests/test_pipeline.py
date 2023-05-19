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
    Netting,
)

ledger = Ledger(
    {
        "cash": Asset(debits=[], credits=[], netting=None),
        "goods_for_sale": Asset(debits=[], credits=[], netting=None),
        "ppe": Asset(
            debits=[],
            credits=[],
            netting=Netting(contra_accounts=["depreciation"], target_name="net_ppe"),
        ),
        "cogs": Expense(debits=[], credits=[], netting=None),
        "sga": Expense(debits=[], credits=[], netting=None),
        "depreciation_expense": Expense(debits=[], credits=[], netting=None),
        "equity": Capital(debits=[], credits=[], netting=None),
        "re": Capital(debits=[], credits=[], netting=None),
        "divp": Liability(debits=[], credits=[], netting=None),
        "sales": Income(
            debits=[],
            credits=[],
            netting=Netting(
                contra_accounts=["discount", "returns"], target_name="net_sales"
            ),
        ),
        "depreciation": ContraAsset(debits=[], credits=[]),
        "discount": ContraIncome(debits=[], credits=[]),
        "returns": ContraIncome(debits=[], credits=[]),
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
