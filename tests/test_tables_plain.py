from abacus.core import AccountBalancesDict, BalanceSheet, IncomeStatement
from abacus import PlainTextViewer

r2 = IncomeStatement(
    income=AccountBalancesDict({"sales": 400}),
    expenses=AccountBalancesDict({"cogs": 200, "sga": 50}),
)
r1 = BalanceSheet(
    assets=AccountBalancesDict({"cash": 1100, "receivables": 0, "goods_for_sale": 50}),
    capital=AccountBalancesDict({"equity": 1000, "re": 75}),
    liabilities=AccountBalancesDict({"divp": 75, "payables": 0}),
)
rename_dict = {
    "re": "Retained earnings",
    "divp": "Dividend due",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}

tv = PlainTextViewer(rename_dict)


def test_plain_text_viewer_on_balance_sheet():
    assert (
        tv.show(r1)
        == "Assets            1150  Capital              1075\n- Cash            1100  - Equity             1000\n- Receivables     0     - Retained earnings    75\n- Goods for sale  50    Liabilities            75\n                        - Dividend due         75\n                        - Payables              0\nTotal             1150  Total                1150"
    )


def test_plain_text_viewer_on_income_statement():
    assert (
        tv.show(r2)
        == "Income                                400\n- Sales                               400\nExpenses                              250\n- Cost of goods sold                  200\n- Selling, general and adm. expenses   50\nProfit                                150"
    )
