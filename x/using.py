import accounts
from base import Entry
from recompose import ChartList, Offset, Reporter, closing_contra_entries, make_chart
import recompose

assert ChartList([]).add("capital:equity").add("contra:equity:ts")["ts"] == Offset(
    name="ts", offsets="equity"
)

x = make_chart("asset:cash", "capital:equity", "contra:equity:ts")
print(x["ts"].__class__)
print(recompose.Offset.__class__)
assert x["ts"] == Offset(name="ts", offsets="equity")
assert x["ts"].as_string("contra") == "contra:equity:ts"
assert x.names() == [
    "current_profit",
    "retained_earnings",
    "null",
    "cash",
    "equity",
    "ts",
]
assert ChartList(x.labels).names() == [
    "current_profit",
    "retained_earnings",
    "null",
    "cash",
    "equity",
]
assert ChartList(x.offsets).names() == ["ts"]
assert x.ledger_dict().keys() == {
    "current_profit",
    "retained_earnings",
    "null",
    "cash",
    "equity",
    "ts",
}
assert x.contra_pairs(accounts.ContraCapital) == [Offset("ts", "equity")]


x.add_many("income:sales", "contra:sales:refunds", "expense:salaries")
ledger = x.ledger()
ledger.post("cash", "equity", 12_000)
ledger.post("ts", "cash", 2_000)
ledger.post("cash", "sales", 3_499)
ledger.post("refunds", "cash", 499)
ledger.post("salaries", "cash", 2_001)
es1 = list(closing_contra_entries(x, ledger, accounts.ContraCapital))
assert es1 == [Entry(debit="equity", credit="ts", amount=2000)]
es2 = list(closing_contra_entries(x, ledger, accounts.ContraIncome))
assert es2 == [Entry(debit="sales", credit="refunds", amount=499)]


r = Reporter(x, ledger)
print(r.tb())
# income statement and balance sheet corrupt initial ledger!
print(r.income_statement())
print(r.balance_sheet())
print(r.trial_balance())
print(r.tb())
