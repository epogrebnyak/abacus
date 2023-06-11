from abacus.accounting_types import BusinessEntry
from abacus.chart import Chart
from abacus.closing import CloseExpense, CloseIncome, CloseISA
from abacus.journal import BaseJournal


def test_base_journal():
    BaseJournal(
        chart=Chart(
            assets=["cash", "receivables", "goods_for_sale"],
            expenses=["cogs", "sga"],
            equity=["equity"],
            liabilities=["divp", "payables"],
            income=["sales"],
            retained_earnings_account="re",
        ),
        starting_balance={},
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
