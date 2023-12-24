from compose import BaseChart, Reporter

chart = BaseChart.use(  # type: ignore
    "asset:cash",  # type: ignore
    "capital:equity",  # type: ignore
    "contra:equity:ts",  # type: ignore
    "income:sales",  # type: ignore
    "contra:sales:refunds",  # type: ignore
    "expense:salaries",  # type: ignore
)  # type: ignore
ledger = chart.ledger()
ledger.post("cash", "equity", 12_000)
ledger.post("ts", "cash", 2_000)
ledger.post("cash", "sales", 3_499)
ledger.post("refunds", "cash", 499)
ledger.post("salaries", "cash", 2_001)
r = Reporter(chart, ledger, titles=dict(ts="treasury stock"))

assert r.trial_balance() == {
    "cash": (10999, 0),
    "ts": (2000, 0),
    "refunds": (499, 0),
    "salaries": (2001, 0),
    "equity": (0, 12000),
    "sales": (0, 3499),
    "retained_earnings": (0, 0),
}
assert r.income_statement().statement.dict() == {
    "income": {"sales": 3000},
    "expenses": {"salaries": 2001},
}
assert r.balance_sheet().statement.dict() == {
    "assets": {"cash": 10999},
    "capital": {"equity": 10000, "retained_earnings": 999},
    "liabilities": {},
}
print(r.trial_balance_viewer())
