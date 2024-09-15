from pydantic import BaseModel


class UserChart(BaseModel):
    assets: list[str] = []
    capital: list[str] = []
    liabilities: list[str] = []
    income: list[str] = []
    expenses: list[str] = []
    retained_earnings: str = ""
    income_summary: str = ""
    contra_accounts: dict[str, list[str]] = {}
    names: dict[str, str] = {}

    def stict(self) -> "Chart":
        from core import ChartDict, Chart, T5

        cd = ChartDict()
        for attrib, t in (
            ("assets", T5.Asset),
            ("capital", T5.Capital),
            ("liabilities", T5.Liability),
            ("income", T5.Income),
            ("expenses", T5.Expense),
        ):
            for name in getattr(self, attrib):
                cd.set(t, name)
        for name, contra_accounts in self.contra_accounts.items():
            for contra_name in contra_accounts:
                cd.offset(name, contra_name)
        return Chart(
            income_summary_account=self.income_summary,
            retained_earnings_account=self.retained_earnings,
            accounts=cd,
        )

    def add(self, attrib, name, title, contra_accounts):
        getattr(self, attrib).append(name)
        self.set_title(name, title)
        for contra_name in contra_accounts:
            self.offset(name, contra_name)

    def add_asset(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("assets", name, title, contra_accounts or [])

    def add_capital(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("capital", name, title, contra_accounts or [])

    def add_liability(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("liabilities", name, title, contra_accounts or [])

    def add_income(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("income", name, title, contra_accounts or [])

    def add_expense(
        self, name: str, title: str = "", contra_accounts: list[str] | None = None
    ):
        self.add("expenses", name, title, contra_accounts or [])

    def offset(self, name: str, contra_name: str | list[str], title: str = ""):
        if name not in self.contra_accounts:
            self.contra_accounts[name] = []
        self.contra_accounts[name].append(contra_name)
        self.title(contra_name, title)

    def set_title(self, name: str, title: str):
        if title:
            self.names[name] = title

    def set_retained_earnings_account(self, name: str):
        self.retained_earnings = name

    def set_income_summary_account(self, name: str):
        self.income_summary = name


from dataclasses import dataclass, field


@dataclass
class Book:
    company: str
    chart: UserChart = field(default_factory=UserChart)


book = Book("Duffin Mills")
book.chart.assets.extend(["cash", "inventory", "ar"])
book.chart.set_title("ar", "Accounts receivable")
book.chart.add_capital("equity")
book.chart.offset("equity", "ts", title="Treasury shares")
book.chart.add_income("sales", contra_accounts=["refunds", "cashback"])
book.chart.add_income("sales", offsets=["refunds", "cashback"])
book.chart.add_expense("cogs", title="Cost of goods sold")
book.chart.add_expense("salaries")
book.chart.add_expense("cit", title="Income tax")
book.chart.add_liability("vat", title="VAT payable")
book.chart.add_liability("dividend")
book.chart.add_liability("cit_due", title="Income tax payable")
book.chart.set_retained_earnings_account("re")
book.chart.set_income_summary_account("_isa")
print(book.chart)
