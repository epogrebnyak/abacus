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
        "depreciation": ContraAsset(debits=[], credits=[250], link="ppe"),
        "discount": ContraIncome(debits=[40, 25], credits=[], link="sales"),
        "returns": ContraIncome(debits=[], credits=[], link="sales"),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
)


def test_closing_entries():
    from abacus.closing import CloseTempContraAccounts, CloseIncome, CloseExpense,CloseISA
    assert closing_entries(ledger) == [CloseTempContraAccounts(dr='sales',
                        cr='discount',
                        amount=65,
                        action='close_tca'),
CloseTempContraAccounts(dr='sales',
                        cr='returns',
                        amount=0,
                        action='close_tca'),
CloseExpense(dr='profit', cr='cogs', amount=180, action='close_expense'),
CloseExpense(dr='profit', cr='sga', amount=50, action='close_expense'),
CloseExpense(dr='profit',
             cr='depreciation_expense',
             amount=250,
             action='close_expense'),
CloseIncome(dr='sales', cr='profit', amount=555, action='close_income'),
CloseISA(dr='profit', cr='re', amount=75, action='close_isa'),
]
