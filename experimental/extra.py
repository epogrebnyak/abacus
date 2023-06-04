from abacus import BalanceSheet, Chart, Entry, IncomeStatement

chart = Chart(
    assets=["cash", "receivables", "goods", "prepaid_rent"],
    expenses=["cogs", "sga"],
    equity=["equity"],  # FIXME: change to capital
    retained_earnings="retained_earnings",
    liabilities=["dividend_payable"],
    income=["sales"],
    contra_accounts={
        "sales": (["discounts, cashback"], "net_sales")
    },  # FIXME:{"sales": ["discounts, cashback"]}
)
starting_balances = {
    "cash": 4500,
    "receivables": 480,
    "equity": 5000,
    "retained_earnings": -20,
}
entries = [
    Entry("prepaid_rent", "cash", 120),  # prepay rent
    Entry("goods", "cash", 1500),  # acquire goods
    Entry("cash", "sales", 750),  # sell some goods
    Entry("cogs", "goods", 500),  # register costs
    Entry("sga", "cash", 100),  # and selling expenses
]
ledger = (
    chart.ledger(**starting_balances)
    .post_entries(entries)
    .adjust(dr="sga", cr="prepaid_rent", amount=90)
    .close_period()
    .postclose(dr="retained_earnings", cr="dividend_payable", amount=75)
)
# check what we've got
assert ledger.balance_sheet() == BalanceSheet(
    assets={"cash": 570},
    capital={"equity": 500, "retained_earnings": 35},
    liabilities={"dividend_payable": 35},
)
assert ledger.income_statement() == IncomeStatement()
