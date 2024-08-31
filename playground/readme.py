from abacus import Book

# Start company
book = Book(company="Pied Piper")

# Create chart of accounts
book.chart.add_assets("cash", "inventory", "ar")
book.chart.add_capital("equity")
book.chart.add_income("sales", offsets=["refunds"])
book.chart.add_expense("cogs")
book.chart.add_liabilities("dividend", "vat")
book.chart.set_retained_earnings("re")

# Open ledger and post entries
# fmt: off
book.open()
book.entries.post("Shareholder investment").amount(300).debit("cash").credit("equity").commit()
book.entries.post("Bought inventory").amount(250).debit("inventory").credit("cash").commit()
book.entries.post("Invoiced customer").debit("ar", 360).credit("sales", 300).credit("vat", 60).commit()
book.entries.post("Shipped goods").amount(200).debit("cogs").credit("inventory").commit()
book.entries.post("Issued partial refund").debit("refunds", 20).credit("ar", 20).commit()
book.entries.post("Accepted payment").amount(180).debit("cash").credit("ar").commit()
# fmt: on

# Close ledger and make post-close entries
book.close()
book.entries.post("Accrue dividend").amount(40).debit("re").credit("dividend").commit()

# Show reports
print(book.balance_sheet.json())
print(book.income_statement.json())
