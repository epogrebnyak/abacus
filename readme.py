from playground.ui import Book

# Start company 
book = Book(company_name="Pied Piper")

# Create chart of accounts
book.add_assets("cash", "inventory", "ar")
book.add_capital("equity")
book.add_income("sales", offsets=["refunds"])
book.add_expense("cogs")
book.add_liability("dividend")
book.set_retained_earnings("re")

# Open ledger and post entries
book.open()
book.entry("Shareholder investment").amount(300).debit("cash").credit("equity").commit()
book.entry("Bought inventory").amount(200).debit("inventory").credit("cash").commit()
book.entry("Invoiced sales").debit("ar", 380).debit("refunds", 20).credit("sales", 400).commit()
book.entry("Shippled goods").amount(200).debit("cogs").credit("inventory").commit()

# Close ledger and make post-close entries
book.close()
book.entry("Accrue dividend").amount(90).debit("re").credit("dividend").commit()

# Show reports
print(book.balance_sheet.json())
print(book.income_statement.json())