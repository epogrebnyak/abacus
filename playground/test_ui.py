from pathlib import Path

import pytest
from ui import AccountBalancesStore, Book, Chart, EntryStore, NamedEntry

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


def test_chart_add_assets():
    chart = Chart().add_asset("cash")
    assert chart.accounts.by_type(T5.Asset) == [("cash", [])]


def test_book():
    book = Book("test")
    book.chart.add_asset("cash")
    book.chart.add_capital("equity")
    book.open()
    (
        book.entry("Shareholder investment")
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
    book = Book("Simple Book, Inc.")
    book.chart.add_asset("cash")
    book.chart.add_asset("cash")
    book.chart.add_capital("equity")
    book.chart.add_income("sales")
    book.chart.add_expense("salary")
    book.open()
    book.entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
    book.entry("Provided services").amount(800).debit("cash").credit("sales").commit()
    book.entry("Paid wages").amount(400).debit("salary").credit("cash").commit()
    return book
# fmt: on


def test_book_is_closed(simple_book):
    assert simple_book.entries.is_closed() is False
    assert simple_book.close().entries.is_closed() is True


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


def test_simple_book_entries_store_apth(simple_book):
    es = EntryStore()
    print(es)
    assert es.directory == Path(".")
    assert es.filename == "entries.json"


def test_trial_balance_after_close(simple_book):
    assert simple_book.close().trial_balance.tuples() == {
        "cash": (1900, 0),
        "equity": (0, 1500),
        "retained_earnings": (0, 400),
    }


def test_entries_store(tmp_path):
    ne = (
        NamedEntry(title="Shareholder investment")
        .amount(1500)
        .debit("cash")
        .credit("equity")
    )
    entries = EntryStore(directory=tmp_path, filename="test.json")
    entries.append(ne)
    _path = entries.to_file()
    print(entries)
    print(_path)
    assert Path(_path).exists()
    assert Path(tmp_path / "test.json").exists()
    b = EntryStore.from_file(tmp_path, "test.json")
    assert b.entries_before_close[0] == double_entry("cash", "equity", 1500).add_title(
        "Shareholder investment"
    )


def test_entries_store_with_simple_book_reloads_after_save(simple_book, tmp_path):
    simple_book.entries.to_file(directory=tmp_path)
    print(simple_book.entries.path)
    print(simple_book.entries.directory)
    print(simple_book.entries.filename)
    a = EntryStore.from_file(directory=tmp_path).entries_before_close
    b = simple_book.entries.entries_before_close
    print(len(a), len(b))
    assert a[0] == b[0]
    assert a[1] == b[1]
    assert a[2] == b[2]
    assert a == b  # tweaked EntryList.__eq__ method for this


def test_closed_simple_book_reloads_after_save(simple_book, tmp_path):
    simple_book.close().save(directory=tmp_path)
    new_book = Book.load("", directory=tmp_path)
    assert simple_book.entries == new_book.entries
    assert simple_book.chart == new_book.chart
    assert simple_book.income_statement == new_book.income_statement
    assert simple_book.balance_sheet == new_book.balance_sheet
    assert simple_book.trial_balance == new_book.trial_balance


@pytest.fixture
def book_after_close():
    book = Book("Lost Data Ltd")
    book.chart.add_asset("cash")
    book.chart.add_income("sales", offsets=["refunds"])
    book.open()
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


def test_opening_balances(tmp_path):
    _book = Book("Duffin Mills")
    _book.chart.add_asset("cash")
    _book.chart.add_capital("equity")
    _book.open()
    _book.double_entry("Shareholder investment", "cash", "equity", 1500).commit()
    _book.account_balances.to_file(directory=tmp_path)
    _book.save(directory=tmp_path)
    book = Book("Duffin Mills")
    book.chart = book.chart.from_file(directory=tmp_path)
    opening_balances = AccountBalancesStore.from_file(directory=tmp_path)
    assert opening_balances.data["cash"] == 1500
    assert opening_balances.data["equity"] == 1500
    book.open(opening_balances={"cash": 1500, "equity": 1500})
    assert book.trial_balance == _book.trial_balance
