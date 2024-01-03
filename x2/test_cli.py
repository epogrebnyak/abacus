import pytest
from cli import Label, Offset, UserChart, extract, Composer
from fine import T, Account, AbacusError
import fine


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
    assert next(extract("актив:каccа", composer)) == Label(T.Asset, "каccа")


@pytest.mark.unit
def test_composer_extract_contra_account_in_russian():
    composer = Composer(contra="контрсчет")
    assert next(extract("контрсчет:ОС:амортизация", composer)) == Offset(
        "ОС", "амортизация"
    )


def test_user_chart_is_convertible():
    assert (
        UserChart("isa", "re", "null")
        .use(
            "asset:cash,ap,inventory,prepaid_rent",
            "capital:equity",
            "contra:equity:ts",
            "income:sales",
            "contra:sales:refunds,voids",
            "expense:salaries,rent",
        )
        .chart()
    )


@pytest.fixture
def chart1():
    return (
        UserChart("isa", "re", "null")
        .use("asset:cash", "capital:equity", "contra:equity:ts")
        .chart()
    )


def test_ledger_dict(chart1):
    assert chart1.ledger() == {
        "cash": fine.Asset(debits=[], credits=[]),
        "equity": fine.Capital(debits=[], credits=[]),
        "ts": fine.ContraCapital(debits=[], credits=[]),
        "re": fine.Capital(debits=[], credits=[]),
        "isa": fine.IncomeSummaryAccount(debits=[], credits=[]),
        "null": fine.NullAccount(debits=[], credits=[]),
    }


def test_assets_property(chart1):
    assert chart1.assets == [Account("cash")]


def test_capital_property(chart1):
    assert chart1.capital == [Account("equity", contra_accounts=["ts"])]


def test_double_append_raises():
    with pytest.raises(AbacusError):
        UserChart("isa", "re", "null").use("asset:cash").use("asset:cash")


def test_double_offset_raises():
    uc = UserChart("isa", "re", "null").use("capital:equity", "contra:equity:ts")
    with pytest.raises(AbacusError):
        uc.use("contra:equity:ts")


def test_no_account_for_offset_raises():
    with pytest.raises(AbacusError):
        UserChart("isa", "re", "null").use("contra:equity:ts")
