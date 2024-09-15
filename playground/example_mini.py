from core import (
    T5,
    BalanceSheet,
    Chart,
    ChartDict,
    Entry,
    IncomeStatement,
    double_entry,
)

cd = ChartDict()
cd.set(T5.Asset, "cash")
cd.set(T5.Capital, "equity")
cd.offset("equity", "treasury_shares")
cd.set(T5.Liability, "vat")
cd.set(T5.Income, "sales")
cd.offset("sales", "refunds")
cd.offset("sales", "voids")
cd.set(T5.Expense, "salaries")
cd.set_isa("isa")
cd.set_re("re")
assert cd.find_contra_accounts("sales") == ["refunds", "voids"]
keys = set(cd.keys())
del cd["isa"]
del cd["re"]
chart = Chart(income_summary_account="isa", retained_earnings_account="re", accounts=cd)
assert "isa" in chart.accounts
assert chart.temporary_accounts == {"isa", "refunds", "sales", "salaries", "voids"}
ledger = chart.accounts.ledger()
assert keys == set(ledger.keys())
entries = [
    double_entry("cash", "equity", 1200),
    double_entry("treasury_shares", "cash", 200),
    Entry().dr("cash", 360).cr("sales", 300).cr("vat", 60),
    double_entry("refunds", "cash", 150),
    double_entry("voids", "cash", 50),
    double_entry("salaries", "cash", 99),
]
ledger.post_many(entries)
assert ledger.trial_balance.tuples() == {
    "cash": (1061, 0),
    "equity": (0, 1200),
    "treasury_shares": (200, 0),
    "sales": (0, 300),
    "refunds": (150, 0),
    "voids": (50, 0),
    "salaries": (99, 0),
    "vat": (0, 60),
    "isa": (0, 0),
    "re": (0, 0),
}

# Close ledger at accounting period end
income_statement = IncomeStatement.new(ledger, chart)
closing_entries = ledger.close(chart)
balance_sheet = BalanceSheet.new(ledger, chart)
print(income_statement)
assert income_statement.net_earnings == 1
print(balance_sheet)

assert ledger.balances() == {
    "cash": 1061,
    "equity": 1200,
    "treasury_shares": 200,
    "vat": 60,
    "re": 1,
}
