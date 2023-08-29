from engine.chart import Chart


def test_empty_chart_constructor():
    assert Chart().dict() == dict(
        assets=[],
        expenses=[],
        equity=[],
        liabilities=[],
        income=[],
        retained_earnings_account="re",
        income_summary_account="current_profit",
        null_account="null",
        contra_accounts={},
        names={},
    )
