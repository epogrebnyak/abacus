from abacus.accounting_types import BusinessEntry, MultipleEntry
from abacus.accounts import ContraAsset, OpenAccount
from abacus.closing import CloseExpense, CloseIncome, CloseISA
from abacus.journal import BaseJournal


def test_base_journal():
    BaseJournal(
        open_accounts=[
            OpenAccount(name="cash", type="Asset"),
            OpenAccount(name="salaries", type="Expense"),
            OpenAccount(name="rent", type="Expense"),
            OpenAccount(name="equity", type="Capital"),
            OpenAccount(name="re", type="RetainedEarnings"),
            OpenAccount(name="services", type="Income"),
            OpenAccount(name="_profit", type="IncomeSummaryAccount"),
        ],
        start_entry=MultipleEntry([], []),
        business_entries=[
            BusinessEntry(dr="rent", cr="cash", amount=200, action="post"),
            BusinessEntry(dr="cash", cr="services", amount=800, action="post"),
            BusinessEntry(dr="salaries", cr="cash", amount=400, action="post"),
        ],
        adjustment_entries=[],
        closing_entries=[
            CloseExpense(
                dr="_profit", cr="salaries", amount=400, action="close_expense"
            ),
            CloseExpense(dr="_profit", cr="rent", amount=200, action="close_expense"),
            CloseIncome(dr="services", cr="_profit", amount=800, action="close_income"),
            CloseISA(dr="_profit", cr="re", amount=200, action="close_isa"),
        ],
        post_close_entries=[],
        is_closed=True,
    )


def test_open_contra():
    oe = OpenAccount("depreciation", "ContraAsset")
    assert oe.new() == ContraAsset(debits=[], credits=[])
