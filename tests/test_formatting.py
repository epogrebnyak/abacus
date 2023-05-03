from abacus.core import BalanceSheet, IncomeStatement, AccountBalancesDict
from abacus.formatting import TextViewer

bs = BalanceSheet(
    assets={"cash": 1130, "receivables": 25, "goods_for_sale": 45},
    capital={"equity": 1000, "re": 75},
    liabilities={"payables": 50, "divp": 75},
)
inc = IncomeStatement(
    income=AccountBalancesDict({"sales": 760}),
    expenses=AccountBalancesDict({"cogs": 440, "sga": 400}),
)
tv = TextViewer(
    dict(
        re="Retained earnings",
        divp="Dividend due",
        cogs="Cost of goods sold",
        sga="Selling, general and adm. expenses",
    )
)


def test_viewers():
    assert (
        tv.balance_sheet(bs)
        == "Assets            1200  Capital              1075\n- Cash            1130  - Equity             1000\n- Receivables       25  - Retained earnings    75\n- Goods for sale    45  Liabilities           125\n                        - Payables             50\n                        - Dividend due         75"
    )
    assert (
        tv.income_statement(inc)
        == "Income                                760  \n- Sales                               760  \nExpenses                              840  \n- Cost of goods sold                  440  \n- Selling, general and adm. expenses  400  \nNet profit                            -80  "
    )
