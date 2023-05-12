from abacus.reports import AccountBalancesDict, BalanceSheet, IncomeStatement


def test_AccountBalanceDict():
    assert (
        AccountBalancesDict(
            [
                ("a", 3),
                ("b", -1),
            ]
        ).total()
        == 2
    )



def test_income_statement(chart0, entries0):
    income_st = chart0.make_ledger().process_entries(entries0).income_statement()
    assert income_st == IncomeStatement(
        income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
    )


def test_balance_sheet_with_close(chart0, entries0):
    balance_st = (
        chart0.make_ledger().process_entries(entries0).close("re").balance_sheet()
    )
    assert balance_st == BalanceSheet(
        assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
        capital={"equity": 1000, "re": 150},
        liabilities={"divp": 0, "payables": 0},
    )


def test_balances(chart0, entries0):
    b = chart0.make_ledger().process_entries(entries0).close("re").balances()
    assert b == {
        "cash": 1100,
        "receivables": 0,
        "goods_for_sale": 50,
        "cogs": 0,
        "sga": 0,
        "equity": 1000,
        "re": 150,
        "divp": 0,
        "payables": 0,
        "sales": 0,
        "profit": 0,
    }
