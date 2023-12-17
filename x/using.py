import accounts
from base import Entry
from compose import (
    BaseLedger,
    ChartList,
    Reporter,
    make_chart,
    close_first,
    close_second,
    close_last,
    chain,
)


def ledger0(x: ChartList) -> BaseLedger:
    ledger = x.ledger()
    ledger.post("cash", "equity", 12_000)
    ledger.post("ts", "cash", 2_000)
    ledger.post("cash", "sales", 3_499)
    ledger.post("refunds", "cash", 499)
    ledger.post("salaries", "cash", 2_001)
    return ledger


# created chart
x = make_chart(
    "asset:cash",
    "capital:equity",
    "contra:equity:ts",
    "income:sales",
    "contra:sales:refunds",
    "expense:salaries",
)
# created ledger
# THIS LEDGER IS EXPECTED TO BE UNCHANGED
ledger = ledger0(x)
assert ledger.data["salaries"].debit_and_credit() == (2001, 0)
assert ledger.data["sales"].debit_and_credit() == (0, 3499)
assert ledger.data["refunds"].debit_and_credit() == (499, 0)

# BUT THE ledger variable get altered by the chain() function
# all of below should print true
ledger2, entries = chain(x, ledger, [close_first, close_second, close_last])
print(ledger.data["salaries"].debit_and_credit() == (2001, 0))
print(ledger.data["sales"].debit_and_credit() == (0, 3499))
print(ledger.data["refunds"].debit_and_credit() == (499, 0))


# r = Reporter(x, ledger=ledger0(x))
# print(r.tb())
# # this should not change
# assert r.tb()["salaries"] == (2001, 0)
# assert r.tb()["sales"] == (0, 3499)
# assert r.tb()["refunds"] == (499, 0)

# # income statement calculation corrupts r.ledger
# r.income_statement()
# print(r.tb()["salaries"] == (2001, 0))
# print(r.tb()["sales"] == (0, 3499))  # must be True, now it is False
# print(r.tb()["refunds"] == (499, 0))  # must be True, now it is False


# # balance sheet calculation corrupts initial ledger further
# r.balance_sheet()
# print(r.tb()["salaries"] == (2001, 0))  # must be True, now it is False
# print(r.tb()["sales"] == (0, 3499))  # must be True, now it is False
# print(r.tb()["refunds"] == (499, 0))  # must be True, now it is False
