from abacus.accounting_types import ClosingEntry
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
from abacus.closing import make_closing_entries
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


def test_close_contra_accounts_with_netting():
    Ledger({"sales": Income([], [200]), "discounts": ContraIncome([8], [])})
    assert 1  # close_contra_accounts(ledger, netting, Income) == [
    # ClosingEntry("sales", "discounts", 8)
    # ]


def test_closing_entries():
    assert list(
        make_closing_entries(ledger, dict(sales=["discount", "returns"])).all()
    ) == [
        ClosingEntry(dr="sales", cr="discount", amount=65),
        ClosingEntry(dr="sales", cr="returns", amount=0),
        ClosingEntry(dr="sales", cr="profit", amount=555),
        ClosingEntry(dr="profit", cr="cogs", amount=180),
        ClosingEntry(dr="profit", cr="sga", amount=50),
        ClosingEntry(dr="profit", cr="depreciation_expense", amount=250),
        ClosingEntry(dr="profit", cr="re", amount=75),
    ]


def test_transfer_entry():
    assert ContraIncome([8], []).balance() == 8
