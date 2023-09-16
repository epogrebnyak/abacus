from abacus.engine.chart import Chart
from abacus.engine.report import BalanceSheet, IncomeStatement

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["divp", "payables"],
    income=["sales"],
)
chart.operations = operations = dict(
    pay_shareholder_capital=("cash", "equity"),
    buy_goods_for_cash=("goods_for_sale", "cash"),
    invoice_buyer=("receivables", "sales"),
    transfer_goods_sold=("cogs", "goods_for_sale"),
    accept_payment=("cash", "receivables"),
    accrue_salary=("sga", "payables"),
    pay_salary=("payables", "cash"),
)
named_entries = [
    # start a company
    ("pay_shareholder_capital", 501),
    ("pay_shareholder_capital", 499),
    # acquire goods
    ("buy_goods_for_cash", 820),
    # one order
    ("invoice_buyer", 600),
    ("transfer_goods_sold", 360),
    ("accept_payment", 549),
    # pay labor
    ("accrue_salary", 400),
    ("pay_salary", 345),
    # another order
    ("invoice_buyer", 160),
    ("transfer_goods_sold", 80),
    ("accept_payment", 80),
]


def fst(xs):
    return [x[0] for x in xs]


def scd(xs):
    return [x[1] for x in xs]


def test_named_entries_income_statement():
    entries = chart.make_entries_for_operations(fst(named_entries), scd(named_entries))
    income_st = chart.ledger().post_many(entries).income_statement(chart)
    assert income_st == IncomeStatement(
        income={"sales": 760}, expenses={"cogs": 440, "sga": 400}
    )


def test_named_entries_balance_sheet():
    entries = chart.make_entries_for_operations(fst(named_entries), scd(named_entries))
    assert chart.ledger().post_many(entries).balance_sheet(chart) == BalanceSheet(
        assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
        capital={"equity": 1000, "re": -80},
        liabilities={"divp": 0, "payables": 55},
    )
