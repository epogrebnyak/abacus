from abacus.reports import BalanceSheet, IncomeStatement
from abacus.tables import RichViewer


def test_cv():
    bs = BalanceSheet(
        assets=({"cash": 1130, "receivables": 25, "goods_for_sale": 45}),
        capital=({"equity": 1000, "re": 75}),
        liabilities=({"payables": 50, "divp": 75}),
    )
    inc = IncomeStatement(
        income=({"sales": 760}),
        expenses=({"cogs": 440, "sga": 400}),
    )

    rename_dict = {
        "re": "Retained earnings",
        "divp": "Dividend due",
        "cogs": "Cost of goods sold",
        "sga": "Selling, general and adm. expenses",
    }
    cv = RichViewer(rename_dict, width=60)
    cv.print(bs)
    cv.print(inc)
