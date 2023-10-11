from abacus import Amount, Entry
from dataclasses import dataclass, field
from datetime import date as Date
from typing import List


@dataclass
class Event:
    title: str

    def entries(self, **kwargs):
        yield Entry


@dataclass
class Transaction:
    amount: Amount
    date: Date = field(default_factory=Date.today)


T = Transaction


@dataclass
class EquityInjection(Event):
    injected: Transaction

    def entries(self, cash_account: str, equity_account: str, **kwargs):
        yield Entry(cash_account, equity_account, self.injected.amount)


@dataclass
class Sales(Event):
    invoiced: Transaction
    cost_registered: Transaction
    payments: List[Transaction] = field(default_factory=list)

    def entries(
        self,
        sales_account: str,
        cos_account: str,
        finished_account: str,
        ar_account: str,
        cash_account: str,
        **kwargs
    ):
        yield Entry(ar_account, sales_account, self.invoiced.amount)
        yield Entry(cos_account, finished_account, self.invoiced.amount)
        for payment in self.payments:
            yield Entry(cash_account, ar_account, payment.amount)


@dataclass
class Purchase(Event):
    purchased: Transaction
    payments: List[Transaction] = field(default_factory=list)

    def entries(
        self, inventory_account: str, ap_account: str, cash_account: str, **kwargs
    ):
        yield Entry(inventory_account, ap_account, self.purchased.amount)
        for payment in self.payments:
            yield Entry(ap_account, cash_account, payment.amount)


@dataclass
class ExpenseSGA(Event):
    expensed: Transaction
    payments: List[Transaction] = field(default_factory=list)

    def entries(self, sga_account: str, ap_account: str, cash_account: str, **kwargs):
        yield Entry(sga_account, ap_account, self.expensed.amount)
        for payment in self.payments:
            yield Entry(ap_account, cash_account, payment.amount)


events = [
    EquityInjection("Initial investment", T(1000)),
    Purchase("Acquired goods for resale", T(800)),
    Sales("Sold goods", T(1200), T(800), [T(1100)]),
    ExpenseSGA("Paid salesmen", T(300), [T(250)]),
]

router_dict = dict(
    cash_account="cash",
    equity_account="equity",
    sales_account="sales",
    cos_account="cos",
    finished_account="goods",
    ar_account="ar",
    inventory_account="goods",
    ap_account="ap",
    sga_account="sga",
)


def unpack_events(events, router_dict):
    return [entry for event in events for entry in event.entries(**router_dict)]


assert unpack_events(events, router_dict) == [
    Entry(debit="cash", credit="equity", amount=1000),
    Entry(debit="goods", credit="ap", amount=800),
    Entry(debit="ar", credit="sales", amount=1200),
    Entry(debit="cos", credit="goods", amount=1200),
    Entry(debit="cash", credit="ar", amount=1100),
    Entry(debit="sga", credit="ap", amount=300),
    Entry(debit="ap", credit="cash", amount=250),
]

# TODO: make repost for events
