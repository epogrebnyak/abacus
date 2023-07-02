from abacus.accounting_types import Entry
from abacus.book import Book, Entries
from abacus.chart import Chart
from abacus.closing import ClosingEntries


def test_post_many():
    chart = (
        Chart(
            assets=["cash", "goods_for_sale"],
            expenses=["cogs", "sga"],
            equity=["equity"],
            income=["sales"],
            liabilities=[],
        )
        .set_retained_earnings("re")
        .offset("sales", ["discounts", "cashback"])
    )

    starting_balances = {"cash": 10, "goods_for_sale": 10, "equity": 20}
    book = chart.book(starting_balances)
    e1 = Entry(dr="cash", cr="equity", amount=1000)  # pay in capital
    e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)  # acquire goods worth 250
    e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)  # sell goods worth 200
    e4 = Entry(cr="sales", dr="cash", amount=400)  # for 400 in cash
    e5 = Entry(cr="cash", dr="sga", amount=50)  # administrative expenses
    book = book.post_many([e1, e2, e3, e4, e5]).close()
    assert book.income_statement().current_profit() == 150


def test_book():
    assert Book(
        chart=Chart(
            assets=["cash", "receivables", "goods_for_sale"],
            expenses=["cogs", "sga"],
            equity=["equity"],
            liabilities=["divp", "payables"],
            income=["sales"],
        ).set_retained_earnings("re"),
        starting_balance={},
        entries=Entries(
            business=[
                Entry(dr="rent", cr="cash", amount=200),
                Entry(dr="cash", cr="services", amount=800),
                Entry(dr="salaries", cr="cash", amount=400),
            ],
            adjustment=[],
            closing=ClosingEntries(),
            post_close=[],
        ),
    )
