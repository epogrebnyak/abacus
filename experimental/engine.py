from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Type

from pydantic import BaseModel

AccountName = str
Amount = int


def permanent():
    return [
        Asset,
        ContraAsset,
        Capital,
        ContraCapital,
        Liability,
        ContraLiability,
        RetainedEarnings,
    ]


class Chart(BaseModel):
    assets: List[AccountName] = []
    expenses: List[AccountName] = []
    equity: List[AccountName] = []
    liabilities: List[AccountName] = []
    income: List[AccountName] = []
    retained_earnings_account: AccountName = "re"
    income_summary_account: AccountName = "current_profit"
    # FIXME: maybe add null account
    contra_accounts: Dict[AccountName, List[AccountName]] = {}

    def mapping(cls):
        """Relate Chart class attributes to actual classes."""
        return dict(
            assets=(Asset, ContraAsset),
            expenses=(Expense, ContraExpense),
            equity=(Capital, ContraCapital),
            liabilities=(Liability, ContraLiability),
            income=(Income, ContraIncome),
        ).items()

    def account_names(self, cls: Type["RegularAccount"]) -> List[AccountName]:
        """Return account name list for regular account class *cls*."""
        reverse_dict = {
            Class.__name__: attribute for attribute, (Class, _) in self.mapping()
        }
        return getattr(self, reverse_dict[cls.__name__])


    def contra_account_pairs(self, cls: Type["RegularAccount"]):
        """Yield pairs of regular and contra account names for given account type *cls*."""
        for regular_account_name, contra_account_names in chart.contra_accounts.items():
            if regular_account_name in chart.account_names(cls):
                for contra_account_name in contra_account_names:
                    yield regular_account_name, contra_account_name




@dataclass
class Entry:
    """Pure accounting entry (without title, date, etc.)"""

    debit: AccountName
    credit: AccountName
    amount: Amount


@dataclass
class TAccount(ABC):
    """Parent class for T-account with debits and credits."""

    debits: List[Amount] = field(default_factory=list)
    credits: List[Amount] = field(default_factory=list)

    @abstractmethod
    def balance(self) -> Amount:
        """Return account balance."""

    def debit(self, amount: Amount):
        """Append *amount* to debit side of the account."""
        self.debits.append(amount)

    def credit(self, amount: Amount):
        """Append *amount* to credit side of the account."""
        self.credits.append(amount)

    def deep_copy(self):
        return self.__class__(self.debits.copy(), self.credits.copy())

    def condense(self):
        cls = self.__class__
        balance = self.balance()
        match self:
            case DebitAccount(_, _):
                return cls([balance], [])
            case CreditAccount(_, _):
                return cls([], [balance])


class DebitAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.debits) - sum(self.credits)


class CreditAccount(TAccount):
    def balance(self) -> Amount:
        return sum(self.credits) - sum(self.debits)


class RegularAccount:
    pass


class Asset(DebitAccount, RegularAccount):
    pass


class Expense(DebitAccount, RegularAccount):
    pass


class Capital(CreditAccount, RegularAccount):
    pass


class Liability(CreditAccount, RegularAccount):
    pass


class Income(CreditAccount, RegularAccount):
    pass


class Unique:
    """There should be just one account of this class in any ledger.
    `IncomeSummaryAccount` and `RetainedEarnings` are unique.
    """


class IncomeSummaryAccount(CreditAccount, Unique):
    pass


class RetainedEarnings(Capital, Unique):
    pass


class ContraAccount:
    pass


class Transferable(ContraAccount, IncomeSummaryAccount):

    def transfer(self, my_name: AccountName, dest_name: AccountName) -> Entry:
        """Make entry to transfer balances from *t_account* of named *this* to *destination* account.
        The entry will differ depending on if *t_account* is debit or credit account."""
        amount = self.balance()
        match self:
            case DebitAccount(_, _):
                return Entry(dest_name, my_name, amount)
            case CreditAccount(_, _):
                return Entry(my_name, dest_name, amount)
            

class ContraAsset(CreditAccount, ContraAccount):
    pass


class ContraExpense(CreditAccount, ContraAccount):
    pass


class ContraCapital(DebitAccount, ContraAccount):
    pass


class ContraLiability(DebitAccount, ContraAccount):
    pass


class ContraIncome(DebitAccount, ContraAccount):
    pass


assert Chart() == Chart(
    assets=[],
    expenses=[],
    equity=[],
    liabilities=[],
    income=[],
    retained_earnings_account="re",
    income_summary_account="current_profit",
    contra_accounts={},
)

if __name__ == "__main__":
    ledger1 = make_ledger(Chart(assets=["cash"], equity=["equity"]))
    post_entry(ledger1, Entry(debit="cash", credit="equity", amount=799))
    post_entry(ledger1, Entry(debit="cash", credit="equity", amount=201))
    assert ledger1["cash"].debits == ledger1["equity"].credits == [799, 201]
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000

    ledger2 = ledger1.deep_copy()
    post_entry(ledger2, Entry(debit="cash", credit="equity", amount=-1000))
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000
    assert ledger2["cash"].balance() == ledger2["equity"].balance() == 0

    @dataclass
    class Job:
        start_ledger: Ledger
        entries: List[Entry]

        def extend(self, entries) -> "Job":
            return Job(self.start_ledger, self.entries + entries)

        def run(self) -> Ledger:
            # FIXME: condense ledger to balances
            res = self.start_ledger.deep_copy()
            post_entries(res, self.entries)
            return res

    @dataclass
    class JobMaker:
        chart: Chart
        entries: "Entries"

        @property
        def ledger0(self):
            """Empty ledger based on *self.chart*."""
            return make_ledger(self.chart)

        def after_start(self):
            return Job(self.ledger0, self.entries.start)

        def after_business(self):
            return Job(self.ledger0, self.entries.start + self.entries.business)

        def after_adjustment(self):
            return Job(
                self.ledger0,
                self.entries.start + self.entries.business + self.entries.adjustment,
            )

        def after_netting_expense_and_income_contra_accounts(self):
            return self.after_adjustment().extend(
                self.entries.closing_contra_income + self.entries.closing_contra_expense
            )

        def before_post_close(self):
            return self.after_netting_expense_and_income_contra_accounts().extend(
                self.entries.closing_income_and_expense + self.entries.closing_isa
            )

        def after_post_close(self):
            """This state of ledger is used to produce balance_sheet."""
            return self.before_post_close().extend(self.entries.post_close)

        def after_netting_expense_and_income_contra_accounts_with_post_close(self):
            """This state of ledger is used to produce income statement."""
            x = self.after_netting_expense_and_income_contra_accounts()
            return x.extend(self.entries.post_close)

    @dataclass
    class UserEntries:
        start: List[Entry]
        business: List[Entry]
        adjustment: List[Entry]
        post_close: List[Entry]

    from typing import Tuple

    def for_reports(chart, entries) -> Tuple[Job, Job]:
        ledger = (
            JobMaker(chart, entries).after_adjustment().run().condense()
        )  # probably takes long
        for_income_statement = Job(
            ledger, entries.closing_contra_income + entries.closing_contra_expense
        )
        for_balance_sheet = for_income_statement.extend(
            entries.closing_income_and_expense + entries.closing_isa
        )
        return for_income_statement, for_balance_sheet

    doc = """
    cash,equity,1000
    goods,cash,800
    cogs,goods,700
    ar,sales,899
    refunds,ar,99
    cash,ar,400
    sga,cash,50
    """

    def to_entries(doc):
        def make(line):
            a, b, c = line.split(",")
            return Entry(a, b, Amount(c))

        return [make(line) for line in doc.strip().split("\n")]

    # Chart -> UserEntries -> ClosingEntries -> (IncomeStatement, BalanceSheet) -> (str, str)

    chart = Chart(
        assets=["cash", "goods", "ar"],
        equity=["equity"],
        income=["sales"],
        expenses=["cogs", "sga"],
        contra_accounts={"sales": ["refunds", "cashback"]},
    )
    entries = to_entries(doc)
    ledger = make_ledger(chart)
    post_entries(ledger, entries)
    print(ledger)
    print(balances(ledger))
    print(ledger)
    assert closing_entries_temp(chart, ledger) == close_contra_income(chart, ledger)
    assert close_contra_expense(chart, ledger) == []
    print(list(flush_contra_accounts(chart, ledger, Expense)))
    print("close rest", closing_entries_rest(chart, ledger))
    post_entries(ledger, closing_entries(chart, ledger))
    print(balances(ledger))
    print(balances(subset(ledger, permanent())))
