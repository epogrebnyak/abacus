from abacus2 import Book, Asset, Capital, Liability, Income, Expense, Account # not implemented

from dataclasses import dataclass, field
from abacus.user_chart import UserChart, make_user_chart
from abacus.core import Entry

def prefix(p, strings):
    return [p+":"+s for s in strings]

@dataclass 
class Book:
    company: str
    chart: UserChart = field(default_factory=make_user_chart)
    entries: list[Entry] = field(default_factory=list)

    def assets(self, *strings):
        self.chart.use(prefix("asset", strings))

    def capital(self, *strings):
        self.chart.use(prefix("capital", strings))

    def liabilities(self, *strings):
        self.chart.use(prefix("liability", strings))

    def income(self, *strings):
        self.chart.use(prefix("income", strings))

    def expenses(self, *strings):
        self.chart.use(prefix("expense", strings))

    def offset(self, a, b):...

    def name(self, a, b):...    
    
book = Book(company="Dragon Trading Company")
Register valid account names and indicate account type
book.chart.allow(
    Asset("cash"),
    Asset("ar", title="Accounts receivable"),
    Capital("equity", title="Shareholder equity"),
    Liability("vat", title="VAT payable"),
    Liability("ap", title="Other accounts payable"),
    Income("services"),
    Expense("salaries"),
    retained_earnings_account=Capital("re"),
)
book.assets("cash", "ar", "inventory")
book.capital("equity")
book.liabilities("vat", "ap")
book.income("services")
book.expenses("salaries")
book.offset("services", "refunds")
book.name("vat", "VAT payable")
book.name("ap", "Other accounts payable")
book.name("ar", "Accounts receivable")

# Regular syntax - post double entry
book.post("Shareholder investment", amount=1500, debit="cash", credit="equity")
# Post multiple entry
book.post_compound(
    "Invoice with VAT", debits=[("ar", 120)], credits=[("sales", 100), ("vat", 20)]
)

# Alternative syntax - does this look better of worse? less Pythonic?
book.debit("cash").credit("equity").post(1500, "Shareholder investment")
book.debit("ar", 120).credit("services", 100).credit("vat", 20).post("Invoice with VAT")

# Close, save and print to screen
book.close_period()
book.report.print()
book.save(chart="./chart.json", store="./entries.linejson")
