import core as core
import pytest
from user_chart import Composer, Label, Offset, user_chart, extract
from core import AbacusError, Account, T


def test_extact_label():
    assert next(extract("asset:cash")) == Label(T.Asset, "cash")


def test_extact_offset():
    assert next(extract("contra:sales:refunds")) == Offset("sales", "refunds")


def test_extact_label_multiple():
    assert list(extract("asset:cash,ap,inventory")) == [
        Label(T.Asset, "cash"),
        Label(T.Asset, "ap"),
        Label(T.Asset, "inventory"),
    ]


@pytest.mark.unit
def test_composer_extract_in_russian():
    composer = Composer().add(T.Asset, "актив")
    assert composer.extract("актив:каccа") == [Label(T.Asset, "каccа")]


@pytest.mark.unit
def test_composer_extract_contra_account_in_russian():
    composer = Composer(contra="контрсчет")
    assert composer.extract("контрсчет:ОС:амортизация") == [Offset("ОС", "амортизация")]


def test_user_chart_is_convertible():
    assert user_chart(
        "asset:cash,ap,inventory,prepaid_rent",
        "capital:equity",
        "contra:equity:ts",
        "income:sales",
        "contra:sales:refunds,voids",
        "expense:salaries,rent",
    ).chart()


@pytest.fixture
def chart1():
    return user_chart("asset:cash", "capital:equity", "contra:equity:ts").chart()


def test_ledger_dict(chart1):
    assert chart1.ledger() == {
        "cash": core.Asset(debits=[], credits=[]),
        "equity": core.Capital(debits=[], credits=[]),
        "ts": core.ContraCapital(debits=[], credits=[]),
        "re": core.Capital(debits=[], credits=[]),
        "isa": core.IncomeSummaryAccount(debits=[], credits=[]),
        "null": core.NullAccount(debits=[], credits=[]),
    }


def test_assets_property(chart1):
    assert chart1.assets == [Account("cash")]


def test_capital_property(chart1):
    assert chart1.capital == [Account("equity", contra_accounts=["ts"])]


def test_double_append_raises():
    with pytest.raises(AbacusError):
        user_chart("asset:cash").use("asset:cash")


def test_double_offset_raises():
    uc = user_chart("capital:equity", "contra:equity:ts")
    with pytest.raises(AbacusError):
        uc.use("contra:equity:ts")


def test_no_account_for_offset_raises():
    with pytest.raises(AbacusError):
        user_chart("isa", "re", "null").use("contra:equity:ts")
