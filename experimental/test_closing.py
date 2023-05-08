from abacus.ledger import Ledger
from abacus.accounts import (
    Asset,
    Netting,
    Expense,
    Capital,
    Liability,
    Income,
    CreditContraAccount,
    DebitContraAccount,
    IncomeSummaryAccount,
)
from abacus.closing import (
    closing_entries,
    closing_entries_for_temporary_contra_acounts,
    closing_entries_income_and_expense_to_isa,
)
from abacus.accounting_types import RenameAccount, Entry

ledger = Ledger(
    {
        "cash": Asset(
            debits=[4000, 620], credits=[3000, 250, 40, 25, 50], netting=None
        ),
        "goods_for_sale": Asset(debits=[250], credits=[180], netting=None),
        "ppe": Asset(
            debits=[3000],
            credits=[],
            netting=Netting(contra_accounts=["depreciation"], target_name="net_ppe"),
        ),
        "cogs": Expense(debits=[180], credits=[], netting=None),
        "sga": Expense(debits=[50], credits=[], netting=None),
        "depreciation_expense": Expense(debits=[250], credits=[], netting=None),
        "equity": Capital(debits=[], credits=[4000], netting=None),
        "re": Capital(debits=[], credits=[], netting=None),
        "divp": Liability(debits=[], credits=[], netting=None),
        "sales": Income(
            debits=[],
            credits=[620],
            netting=Netting(
                contra_accounts=["discount", "returns"], target_name="net_sales"
            ),
        ),
        "depreciation": CreditContraAccount(debits=[], credits=[250]),
        "discount": DebitContraAccount(debits=[40, 25], credits=[]),
        "returns": DebitContraAccount(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }
)


def test_closing_entries():
    assert closing_entries(ledger, "re") == [
        Entry(dr="sales", cr="discount", amount=65),
        Entry(dr="sales", cr="returns", amount=0),
        RenameAccount(existing_name="sales", new_name="net_sales"),
        Entry(dr="net_sales", cr="profit", amount=555),
        Entry(dr="profit", cr="cogs", amount=180),
        Entry(dr="profit", cr="sga", amount=50),
        Entry(dr="profit", cr="depreciation_expense", amount=250),
        Entry(dr="profit", cr="re", amount=75),
    ]