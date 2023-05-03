from abacus.core import BalanceSheet, AccountBalancesDict, IncomeStatement
from abacus.tables import ConsoleViewer


def test_cv():
    bs = BalanceSheet(
        assets=AccountBalancesDict(
            {"cash": 1130, "receivables": 25, "goods_for_sale": 45}
        ),
        capital=AccountBalancesDict({"equity": 1000, "re": 75}),
        liabilities=AccountBalancesDict({"payables": 50, "divp": 75}),
    )
    inc = IncomeStatement(
        income=AccountBalancesDict({"sales": 760}),
        expenses=AccountBalancesDict({"cogs": 440, "sga": 400}),
    )

    rename_dict = {
        "re": "Retained earnings",
        "divp": "Dividend due",
        "cogs": "Cost of goods sold",
        "sga": "Selling, general and adm. expenses",
    }
    cv = ConsoleViewer(rename_dict, width=60)
    cv.print(bs)
    cv.print(inc)
