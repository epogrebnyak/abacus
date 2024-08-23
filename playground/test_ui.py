from pathlib import Path

import pytest
from ui import Book, EntryStore, NamedEntry

from core import T5, Amount, IncomeStatement, double_entry


def test_named_entry_constructor():
    ne = (
        NamedEntry(title="Shareholder investment")
        .amount(300)
        .debit(account_name="cash")
        .credit(account_name="equity")
    )
    assert ne.debits == [("cash", Amount(300))]
    assert ne.credits == [("equity", Amount(300))]
    assert ne.title == "Shareholder investment"


def test_named_entry_on_None_amount_raises_error():
    with pytest.raises(TypeError):
        NamedEntry().debit(account_name="cash")


def test_book_add_assets():
    xs = Book("Pied Piper").add_asset("cash").chart[T5.Asset]
    xs[0] == ("cash", [])


def test_book():
    book = (
        Book("test")
        .add_asset("cash")
        .add_capital("equity")
        .open()
        .entry("Shareholder investment")
        .amount(1500)
        .debit("cash")
        .credit("equity")
        .commit()
    )
    assert book.entries.entries_before_close[-1] == NamedEntry(
        title="Shareholder investment",
        debits=[("cash", Amount(1500))],
        credits=[("equity", Amount(1500))],
    )


# fmt: off
@pytest.fixture
def simple_book():
       return (
        Book("Simple Book, Inc.")
        .add_asset("cash")
        .add_capital("equity")
        .add_income("sales")
        .add_expense("salary")
        .open()
        .entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
        .entry("Provided services").amount(800).debit("cash").credit("sales").commit()
        .entry("Paid wages").amount(400).debit("salary").credit("cash").commit()
    )
# fmt: on


def test_book_is_closed(simple_book):
    assert simple_book.is_closed() is False
    assert simple_book.close().is_closed() is True


def test_income_statement_before_close(simple_book):
    assert simple_book.income_statement.net_earnings == 400


def test_income_statement_after_close(simple_book):
    assert simple_book.close().income_statement.net_earnings == 400


def test_balance_sheet_before_close(simple_book):
    assert simple_book.balance_sheet.assets["cash"] == 1900
    assert simple_book.balance_sheet.capital["equity"] == 1500
    assert (
        simple_book.balance_sheet.capital["retained_earnings"] == 0
    )  # may need proxy value of 400
    assert simple_book.balance_sheet.liabilities == {}


def test_balance_sheet_after_close(simple_book):
    assert simple_book.close().balance_sheet.assets["cash"] == 1900
    assert simple_book.balance_sheet.capital["equity"] == 1500
    assert simple_book.balance_sheet.capital["retained_earnings"] == 400
    assert simple_book.balance_sheet.liabilities == {}


def test_trial_balance_before_close(simple_book):
    assert simple_book.trial_balance.tuples() == {
        "cash": (1900, 0),
        "equity": (0, 1500),
        "sales": (0, 800),
        "salary": (400, 0),
        "__isa__": (0, 0),
        "retained_earnings": (0, 0),
    }


def test_trial_balance_after_close(simple_book):
    assert simple_book.close().trial_balance.tuples() == {
        "cash": (1900, 0),
        "equity": (0, 1500),
        "retained_earnings": (0, 400),
    }


@pytest.fixture
def tmp_json(tmp_path):
    return Path(tmp_path / "test.json")


def test_entry_store(tmp_json):
    a = (
        EntryStore()
        .set_path(tmp_json)
        .head("Start business")
        .amount(500)
        .debit("cash")
        .credit("equity")
        .commit()
    )
    a.to_file()
    b = EntryStore.from_file(path=tmp_json)
    assert b.entries_before_close[0] == double_entry("cash", "equity", 500).add_title(
        "Start business"
    )


def test_entry_store_with_simple_book_reloads_after_save(simple_book, tmp_json):
    simple_book.entries.to_file(path=tmp_json)
    a = EntryStore.from_file(tmp_json).entries_before_close
    b = simple_book.entries.entries_before_close
    print(len(a), len(b))
    assert a[0] == b[0]
    assert a[1] == b[1]
    assert a[2] == b[2]
    assert a == b  # tweaked EntryList.__eq__ method for this


def test_closed_simple_book_reloads_after_save(simple_book, tmp_json):
    simple_book.close().save()
    new_book = Book.load("")
    assert simple_book.entries == new_book.entries
    assert simple_book.chart == new_book.chart
    assert simple_book.income_statement == new_book.income_statement
    assert simple_book.balance_sheet == new_book.balance_sheet
    assert simple_book.trial_balance == new_book.trial_balance


@pytest.fixture
def book_after_close():
    book = (
        Book("Lost Data Ltd")
        .add_asset("cash")
        .add_income("sales", offsets=["refunds"])
        .open()
    )
    book.double_entry("Regiter sales", "cash", "sales", 5).commit()
    book.double_entry("Issue refund", "refunds", "cash", 3).commit()
    book.close()
    return book


def test_income_statement_after_close_again(book_after_close):
    ref = IncomeStatement(income={"sales": 2}, expenses={})
    assert book_after_close.income_statement == ref


def test_income_statement_after_save_and_load(book_after_close):
    ref = IncomeStatement(income={"sales": 2}, expenses={})
    assert book_after_close.save().load("Lost Data Ltd").income_statement == ref
