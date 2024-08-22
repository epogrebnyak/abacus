from abacus import Book

# Start company
book = Book(company="Pied Piper")

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
print(book.trial_balance.tuples())
print(book._ledger)
book.entry("Invoiced sales").debit("ar", 400).credit("sales", 400).commit()
book.entry("Shipped goods").amount(200).debit("cogs").credit("inventory").commit()
book.entry("Issued partial refund").debit("refunds", 40).credit("ar", 40).commit()
# FIXME:
# core.AbacusError: {'Could not post to ledger (negative balance)': 
# [NamedEntry(debits=[('cogs', Decimal('160'))], credits=[('inventory', Decimal('160'))], title='Accepted payment')]}
book.entry("Accepted payment").amount(160).debit("cogs").credit("inventory").commit()

# Close ledger and make post-close entries
book.close()
book.entry("Accrue dividend").amount(90).debit("re").credit("dividend").commit()

# Show reports
print(book.balance_sheet.json())
print(book.income_statement.json())
