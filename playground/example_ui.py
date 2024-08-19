from ui import Book, StoredEntry

book = Book("Duffin Mills")
book.add_assets("cash", "ar", "inventory")
book.add_capital("equity").offset("buyback")
book.add_income("sales").offset("refunds", "cashback")
book.add_expenses("cogs", "salaries")
book.add_liabilities("vat", "dividend")
book.set_retained_earnings_account("re")
book.open()
# fmt: off
n = 1
for _ in range(1):
    book.entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
    book.entry("Bought inventory").amount(1000).debit("inventory").credit("cash").commit()
    book.entry("Invoiced sales with VAT").debit("ar", 1200).credit("sales", 1000).credit("vat", 200).commit()
    book.entry("Registered costs").amount(600).debit("cogs").credit("inventory").commit()
    book.entry("Accepted payment").amount(900).credit("ar").debit("cash").commit()
    book.entry("Made refund").amount(50).debit("refunds").credit("ar").commit()
    book.entry("Made cashback").amount(50).debit("cashback").credit("cash").commit()
    book.entry("Paid salaries").amount(150).credit("cash").debit("salaries").commit()
book.close()
book.entry("Bought back shares").amount(100).debit("buyback").credit("cash").commit()
book.entry("Announced dividend").amount(100).debit("re").credit("dividend").commit()
# fmt: on
if n == 1:
    assert book._current_id == 10
    print((a := book.income_statement).json())
    assert a == {"income": {"sales": 900}, "expenses": {"cogs": 600, "salaries": 150}}
    print((b := book.balance_sheet).json())
    assert b == {
        "assets": {"cash": 1100, "ar": 250, "inventory": 400},
        "capital": {"equity": 1400, "re": 50},
        "liabilities": {"vat": 200, "dividend": 100},
    }


assert book.entries[-1] == StoredEntry(
    title="Announced dividend", debits=[("re", 100)], credits=[("dividend", 100)]
)
