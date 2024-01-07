from viewers import BS, IS, ViewerBS, ViewerIS, ViewerTB
from abacus.core import AccountBalances as AB


def test_viewer_bs():
    b = BS(
        assets=AB(cash=200),
        capital=AB(equity=150, retained_earnings=-20),
        liabilities=AB(loan=65, dd=5),
    )
    vb = ViewerBS(
        b,
        rename_dict=dict(
            assets="активы", cash="касса", dd="dividend due", total="итого"
        ),
        title="Баланс",
    )
    assert len(str(vb)) > 0
    assert "Итого" in str(vb)
    assert vb.width == 38
    vb.print()
    vb.print(80)


def test_viewer_is():
    i = IS(income=AB(sales=40), expenses=AB(rent=25, salaries=35))
    vi = ViewerIS(i, "Income statement")
    assert "Income statement" in str(vi)
    vi.print()
    vi.print(80)


def test_viewer_tb():
    vtb = ViewerTB(dict(cash=(100, 0), equity=(0, 120), re=(0, -20)))
    assert "cash" in str(vtb)
    vtb.print()
    vtb.print(80)
