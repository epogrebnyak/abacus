from compose import BaseChart, BaseLedger, Pipeline, Reporter, make_chart


def ledger0(x: BaseChart) -> BaseLedger:
    ledger = x.ledger()
    ledger.post("cash", "equity", 12_000)
    ledger.post("ts", "cash", 2_000)
    ledger.post("cash", "sales", 3_499)
    ledger.post("refunds", "cash", 499)
    ledger.post("salaries", "cash", 2_001)
    return ledger


# created chart
x = make_chart(  # type: ignore
    "asset:cash",  # type: ignore
    "capital:equity",  # type: ignore
    "contra:equity:ts",  # type: ignore
    "income:sales",  # type: ignore
    "contra:sales:refunds",  # type: ignore
)  # type: ignore
# created ledger
# THIS LEDGER IS EXPECTED TO BE UNCHANGED
ledger = ledger0(x)
assert ledger.data["salaries"].debit_and_credit() == (2001, 0)
assert ledger.data["sales"].debit_and_credit() == (0, 3499)
assert ledger.data["refunds"].debit_and_credit() == (499, 0)

# BUT THE ledger variable get altered by the chain() function
# all of below should print true
Pipeline(x, ledger).close_first().close_second().close_last()
print(ledger.data["salaries"].debit_and_credit() == (2001, 0))
print(ledger.data["sales"].debit_and_credit() == (0, 3499))
print(ledger.data["refunds"].debit_and_credit() == (499, 0))


r = Reporter(x, ledger=ledger0(x))
print(r.tb())
# this should not change
assert r.tb()["salaries"] == (2001, 0)
assert r.tb()["sales"] == (0, 3499)
assert r.tb()["refunds"] == (499, 0)

# income statement calculation corrupts r.ledger
print(r.income_statement())
print(r.tb()["salaries"] == (2001, 0))
print(r.tb()["sales"] == (0, 3499))  # must be True, now it is False
print(r.tb()["refunds"] == (499, 0))  # must be True, now it is False


# balance sheet calculation corrupts initial ledger further
print(r.balance_sheet())
print(r.tb()["salaries"] == (2001, 0))  # must be True, now it is False
print(r.tb()["sales"] == (0, 3499))  # must be True, now it is False
print(r.tb()["refunds"] == (499, 0))  # must be True, now it is False
print(r.tb())
