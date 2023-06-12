from abacus.accounts import (Asset, Capital, ContraAsset, ContraIncome,
                             Expense, Income, IncomeSummaryAccount, Liability,
                             RetainedEarnings)
from abacus.closing import close_contra_accounts, closing_entries
from abacus.closing_types import CloseContraIncome
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
    ledger = Ledger({"sales": Income([], [200]), "discounts": ContraIncome([8], [])})
    netting = {"sales": ["discounts"]}
    assert close_contra_accounts(ledger, netting, Income) == [
        CloseContraIncome("sales", "discounts", 8)
    ]


def test_closing_entries():
    from abacus.closing import CloseExpense, CloseIncome, CloseISA
    from abacus.closing_types import CloseContraIncome

    assert closing_entries(ledger, dict(sales=["discount", "returns"])) == [
        CloseContraIncome(
            dr="sales", cr="discount", amount=65, action="close_contra_income"
        ),
        CloseContraIncome(
            dr="sales", cr="returns", amount=0, action="close_contra_income"
        ),
        CloseIncome(dr="sales", cr="profit", amount=555, action="close_income"),
        CloseExpense(dr="profit", cr="cogs", amount=180, action="close_expense"),
        CloseExpense(dr="profit", cr="sga", amount=50, action="close_expense"),
        CloseExpense(
            dr="profit", cr="depreciation_expense", amount=250, action="close_expense"
        ),
        CloseISA(dr="profit", cr="re", amount=75, action="close_isa"),
    ]
