from core import (
    T5,
    BalanceSheet,
    Chart,
    Chart,
    Entry,
    IncomeStatement,
    double_entry,
)

cd = Chart("isa", "re")
cd.set(T5.Asset, "cash")
cd.set(T5.Capital, "equity")
cd.offset("equity", "treasury_shares")
cd.set(T5.Liability, "vat")
cd.set(T5.Income, "sales")
cd.offset("sales", "refunds")
cd.offset("sales", "voids")
cd.set(T5.Expense, "salaries")
assert cd.find_contra_accounts("sales") == ["refunds", "voids"]
assert cd.closing_pairs == [
    ("refunds", "sales"),
    ("voids", "sales"),
    ("sales", "isa"),
    ("salaries", "isa"),
    ("isa", "re"),
]

assert cd.temporary_accounts == {"isa", "refunds", "sales", "salaries", "voids"}
ledger = cd.ledger()
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
income_statement = IncomeStatement.new(ledger, cd)
closing_entries = ledger.close(cd)
balance_sheet = BalanceSheet.new(ledger, cd)
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
