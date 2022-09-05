from abacus.nameit import Chart

chart = Chart(
    assets=dict(
        cash="Cash and equivalents",
        inv="Inventory",
    ),
    expenses=dict(
        cogs="Cost of goods sold (COGS)",
        int="Interest",
    ),
    capital=dict(eq="Shareholder equity"),
    liabilities=dict(debt="Debt", ip="Interest payable"),
    income=dict(sales="Sales"),
)

chart_dict = {
    "assets": {"cash": "Cash and equivalents", "inv": "Inventory"},
    "expenses": {"cogs": "Cost of goods sold (COGS)", "int": "Interest"},
    "capital": {"eq": "Shareholder equity"},
    "liabilities": {"debt": "Debt", "ip": "Interest payable"},
    "income": {"sales": "Sales"},
}


def test_chart():
    assert chart == Chart(**chart_dict)


from abacus.nameit import (
    Asset,
    Capital,
    Entry,
    Expense,
    Income,
    Liability,
    make_ledger,
    process,
    profit,
)

account_dict = dict(
    cash=Asset("Cash and equivalents"),
    inv=Asset("Inventory"),
    cogs=Expense("Cost of goods sold (COGS)"),
    int=Expense("Interest"),
    eq=Capital("Shareholder equity"),
    debt=Liability("Debt"),
    ip=Liability("Interest payable"),
    sales=Income("Sales"),
)


def test_make_ledger():
    assert make_ledger(chart) == account_dict


entries = [
    Entry(200, "cash", "eq"),
    Entry(800, "cash", "debt"),
    Entry(500, "inv", "cash"),
    Entry(500, "cogs", "inv"),
    Entry(620, "cash", "sales"),
    Entry(80, "int", "ip"),
]


def test_profit():
    account_dict2 = process(account_dict, entries)
    assert 40 == profit(account_dict2).amount


from abacus.nameit import Balance, Line, left, make_balance, right


def tets_account_dict_to_balance():
    account_dict2 = process(account_dict, entries)
    b = make_balance(account_dict2)
    pass


# %%

b = Balance(
    assets=[
        Line(text="Cash and equivalents", amount=1120),
        Line(text="Inventory", amount=0),
    ],
    capital=[Line(text="Shareholder equity", amount=200)],
    liabilities=[
        Line(text="Debt", amount=800),
        Line(text="Interest payable", amount=80),
    ],
    current_profit=Line(text="Current profit", amount=40),
)


def test_left():
    assert left(b) == [
        "Assets",
        "  Cash and equivalents... 1120",
        "  Inventory..............    0",
    ]


def test_right():
    assert right(b) == [
        "Capital",
        "  Shareholder equity... 200",
        "  Current profit.......  40",
        "Liabilities",
        "  Debt................. 800",
        "  Interest payable.....  80",
    ]
