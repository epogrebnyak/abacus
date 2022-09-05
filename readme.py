from abacus import Chart, Entry, Book, make_ledger

chart = Chart(
    assets=["cash", "goods"],
    equity=["equity", "retained_earnings"],
    liabilities=["debt", "payables"],
    income=["sales"],
    expenses=["cogs", "interest"],
)

L = make_ledger(chart)

entries = [
    Entry(
        debit="cash",
        credit="equity",
        value=20,
        description="Shareholders paid in capital in cash.",
    ),
    Entry(debit="cash", credit="debt", value=80, description="Firm got a loan."),
    Entry(
        debit="goods",
        credit="cash",
        value=50,
        description="Bought some goods for resale.",
    ),
    Entry(
        debit="cash",
        credit="sales",
        value=75,
        description="Sold goods worth 40 for 75, got more cash.",
    ),
    Entry(
        debit="cogs",
        credit="goods",
        value=40,
        description="Accounted expenses for goods sold.",
    ),
    Entry(debit="interest", credit="cash", value=8, description="Paid 10% interest."),
    Entry(
        debit="debt", credit="cash", value=40, description="Paid off half of the debt."
    ),
]

for e in entries:
    L.process(e)

b = Book(chart, L)
print(b)
