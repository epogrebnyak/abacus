from abacus.core import AccountBalances, BalanceSheet, IncomeStatement, TrialBalance


def test_balance_sheet_viewers():
    b = BalanceSheet(
        assets=AccountBalances({"cash": 110}),
        capital=AccountBalances({"equity": 100, "re": 10}),
        liabilities=AccountBalances({"dividend_due": 0}),
    )
    assert b.viewer(rich=False).print() is None
    assert b.viewer(rich=True).print() is None


def test_income_statement_viewers():
    i = IncomeStatement(
        income=AccountBalances({"sales": 40}),
        expenses=AccountBalances({"salaries": 30}),
    )
    assert i.viewer(rich=False).print() is None
    assert i.viewer(rich=True).print() is None


def test_trial_balance_viewer():
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
    t.viewer().print()


def test_print_all():
    from abacus import Chart, Report

    chart = Chart(
        assets=["cash"],
        capital=["equity"],
        income=["services"],
        expenses=["marketing", "salaries"],
    )

    # Create a ledger using the chart
    ledger = chart.ledger()

    # Post entries to ledger
    ledger.post(debit="cash", credit="equity", amount=5000)
    ledger.post(debit="marketing", credit="cash", amount=1000)
    ledger.post(debit="cash", credit="services", amount=3499)
    ledger.post(debit="salaries", credit="cash", amount=2000)

    # Print trial balance, balance sheet and income statement
    report = Report(chart, ledger).rename("re", "Retained earnings")
    assert report.print_all() is None
