from abacus import Chart, IncomeStatement, BalanceSheet

# Create chart of accounts
chart = Chart(
    assets=["cash"],
    equity=["equity"],
    retained_earnings_account="re",
    expenses=["salaries", "rent"],
    income=["services"],
)

# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
journal = (
    chart.journal(**starting_balances)
    .post(dr="rent", cr="cash", amount=200)
    .post(dr="cash", cr="services", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
    .close()  # not implemented
)


def test_postings():
    assert journal.data == []


def test_balance_sheet():
    assert journal.balance_sheet() == BalanceSheet(
        assets={"cash": 1600}, capital={"equity": 1500, "re": 100}, liabilities={}
    )


def test_balances():
    assert journal.balances() == {
        "_profit": 0,
        "cash": 1600,
        "equity": 1500,
        "re": 100,
        "rent": 0,
        "salaries": 0,
        "services": 0,
    }


def test_current_balances_n():
    assert journal.current_profit() == 200


def test_income_statement():
    assert journal.income_statement() == IncomeStatement(
        income={"services": 800}, expenses={"salaries": 400, "rent": 200}
    )
