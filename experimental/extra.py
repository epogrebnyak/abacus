from abacus import BalanceSheet, Chart, Entry, IncomeStatement

chart = Chart(
    assets=["cash", "goods", "ppe", "prepaid_expenses"],
    expenses=["cogs", "sga.services", "sga.salaries", "sga.d"],
    equity=["equity"],
    retained_earnings_account="retained_earnings",
    liabilities=["dividend_payable"],
    income=["sales"],
    contra_accounts={"sales": ["discounts", "cashback"], "ppe": ["depreciation"]},
)
starting_balances = {
    "cash": 500,
    "ppe": 3500,
    "goods": 1000,
    "equity": 4200,
    "retained_earnings": 800,
}
entries = [
    Entry("prepaid_expenses", "cash", 120),  # prepay rent
    Entry("cash", "sales", 850),  # sell some goods
    Entry("discounts", "cash", 75),
    Entry("cashback", "cash", 25),
    Entry("cogs", "goods", 300),  # register cost of sales
    Entry("sga.d", "depreciation", 250),  # add depreciation
    Entry("sga.salaries", "cash", 200),  # and selling expenses
    Entry("sga.services", "prepaid_expenses", 80),  # adjust services
]

from pprint import pprint

journal = (
    chart.journal(**starting_balances)
    .post_entries(entries)
    .close()
    #      .post_close(dr="retained_earnings", cr="dividend_payable", amount=75)
)

# check what we've got
pprint(starting_balances)
pprint(journal.balance_sheet())
pprint(journal.income_statement())
pprint(journal.current_profit())

# TODO: convert to test.
