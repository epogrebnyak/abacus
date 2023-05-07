# %%
from abacus import Chart
from abacus.core import Amount, AccountName
from abacus.accounting_types import Account, AccountBalancesDict
from dataclasses import dataclass
from typing import Optional, Dict, List


chart = Chart(
    assets=["ppe"],
    expenses=[],
    equity=[],
    liabilities=[],
    income=["sales"],
    debit_contra_accounts=[("discounts", "sales")],
    credit_contra_accounts=[("depr", "ppe")],
)

ledger = chart.make_ledger()
print(ledger)

# %%


def test_invalid_contra_account():
    import pytest

    with pytest.raises(ValueError):
        Chart(
            assets=["ppe"],
            expenses=[],
            equity=[],
            liabilities=[],
            income=["sales"],
            debit_contra_accounts=[],
            credit_contra_accounts=[("abc", "zzz")],
        )


@dataclass
class Saldo:
    """Account balance (in Italian and some other languages)."""

    amount: Amount
    nets_with: Optional[AccountName] = None

    def __sub__(self, amount: Amount):
        return self.__class__(self.amount - amount)


class DebitSaldo(Saldo):
    pass


class CreditSaldo(Saldo):
    pass


TrialBalance = Dict[AccountName, Saldo]
Ledger = Dict[AccountName, Account]


# Chart -> Dict[str, Account] -> Dict[str, Saldo]

tb = dict(
    ppe=DebitSaldo(1000),
    sales=CreditSaldo(300),
    discounts=DebitSaldo(25, "sales"),
    depr=CreditSaldo(600, "ppe"),
)


def netting(tb: TrialBalance) -> TrialBalance:
    res = {}
    # create target accounts (like 'ppe')
    for account_name, saldo in tb.items():
        if not saldo.nets_with:
            res[account_name] = saldo
    # work with accounts netted to zero (like 'depr')
    # we do not include these zero accounts in netting() output
    for account_name, saldo in tb.items():
        if saldo.nets_with:
            match saldo, res[saldo.nets_with]:
                case DebitSaldo(amount, nets_with), CreditSaldo(_, _):
                    res[nets_with] -= amount
                case CreditSaldo(amount, nets_with), DebitSaldo(_, _):
                    res[nets_with] -= amount
                case (_, _):
                    raise ValueError([saldo, res[saldo.nets_with]])
    return res


def flush(tb: TrialBalance) -> AccountBalancesDict:
    """Discard credit or debit side inofrmation."""
    return AccountBalancesDict((name, saldo.amount) for name, saldo in tb.items())


print(flush(netting(tb)))


def test_tb_twice():
    # must test twice - dictionaries may fail deep copying
    assert flush(netting(tb)) == AccountBalancesDict({"ppe": 400, "sales": 275})
    assert flush(netting(tb)) == AccountBalancesDict({"ppe": 400, "sales": 275})
