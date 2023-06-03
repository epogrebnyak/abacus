from abacus.accounting_types import Entry
from abacus.accounts import (
    Asset,
    Capital,
    ContraAsset,
    ContraIncome,
    Expense,
    Income,
    IncomeSummaryAccount,
    Liability,
    RetainedEarnings,
)
from abacus.closing import closing_entries
from abacus.ledger import Ledger

ledger = Ledger(
    {
        "cash": Asset(debits=[4000, 620], credits=[3000, 250, 40, 25, 50]),
        "goods_for_sale": Asset(debits=[250], credits=[180]),
        "ppe": Asset(
            debits=[3000],
            credits=[],
        ),
        "cogs": Expense(debits=[180], credits=[]),
        "sga": Expense(debits=[50], credits=[]),
        "depreciation_expense": Expense(debits=[250], credits=[]),
        "equity": Capital(debits=[], credits=[4000]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "divp": Liability(debits=[], credits=[]),
        "sales": Income(
            debits=[],
            credits=[620],
        ),
        "depreciation": ContraAsset(debits=[], credits=[250]),
        "discount": ContraIncome(debits=[40, 25], credits=[]),
        "returns": ContraIncome(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
)


def test_closing_entries():
    assert closing_entries(ledger) == [
        Entry(dr="sales", cr="discount", amount=65),
        Entry(dr="sales", cr="returns", amount=0),
        RenameAccount(existing_name="sales", new_name="net_sales"),
        Entry(dr="net_sales", cr="profit", amount=555),
        Entry(dr="profit", cr="cogs", amount=180),
        Entry(dr="profit", cr="sga", amount=50),
        Entry(dr="profit", cr="depreciation_expense", amount=250),
        Entry(dr="profit", cr="re", amount=75),
    ]
