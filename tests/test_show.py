from abacus.core import AccountBalances, BalanceSheet, IncomeStatement, TrialBalance
from abacus.show import show
from abacus.show_rich import rich_print


def test_show_and_rich_print_are_callable():
    b = BalanceSheet(
        assets=AccountBalances({"cash": 110}),
        capital=AccountBalances({"equity": 100, "re": 10}),
        liabilities=AccountBalances({"dividend_due": 0}),
    )
    print(show(b))
    i = IncomeStatement(
        income=AccountBalances({"sales": 40}),
        expenses=AccountBalances({"salaries": 30}),
    )
    print(show(i))
    t = TrialBalance(
        {
            "cash": (110, 0),
            "ts": (20, 0),
            "refunds": (5, 0),
            "voids": (2, 0),
            "salaries": (30, 0),
            "equity": (0, 120),
            "re": (0, 0),
            "dividend_due": (0, 0),
            "sales": (0, 47),
            "isa": (0, 0),
            "null": (0, 0),
        }
    )
    print(show(t))
    rich_print(b)
    rich_print(i)
