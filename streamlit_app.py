# How to run:
#
# git clone https://github.com/epogrebnyak/abacus.git
# pip install -e .
# streamlit run streamlit_app.py
#
# Что сделать: TODO-1, TODO-2.
#
import streamlit as st

if "entries" not in st.session_state:
    st.session_state["entries"] = []


def add_entry(dr, cr, a):
    st.session_state["entries"] += [Entry(dr, cr, a)]


def to_int(a):
    try:
        return int(a)
    except ValueError:
        return 0


def last_posted_caption():
    es = st.session_state["entries"]
    if not es:
        st.caption("Nothing posted yet.")
    else:
        e = es[-1]
        st.caption(f"Last posted: {e.debit}, {e.credit}, {e.amount}")


labels = ["cash", "ar", "inventory", "equity", "sales", "cogs", "sga"]
with st.sidebar:
    st.header("Post double entry")
    with st.form("add_entry"):
        dr = st.selectbox("Debit:", labels, index=0)
        cr = st.selectbox("Credit:", labels, index=3)
        a = to_int(st.text_input("Amount (only integer)"))
        st.form_submit_button(label="Post entry", on_click=add_entry, args=(dr, cr, a))
        # TODO-2: My scenario:
        #         - I run the app
        #         - I add amount 500, then click Post entry button
        #           expected to see is (cash, equity, 500), but I get
        #           (cash, equity, 500) - which I never submitted.
        #         - I add amount 200, then click Post entry button,
        #         - after this I see (cash, equity, 500), so
        #           last_posted_caption() lags to show value by one click.
        #           Very strange!
        last_posted_caption()


st.header("Accounting with `abacus` :star:")

from abacus import Chart, Report
from abacus.core import Entry
from abacus.user_chart import UserChart

chart = Chart(
    assets=["cash", "ar", "inventory"],
    capital=["equity"],
    income=["sales"],
    expenses=["cogs", "sga"],
)
ledger = chart.ledger()
ledger.post(debit="cash", credit="equity", amount=20001, title="Owner's investment")
report = Report(
    chart,
    ledger,
    rename_dict=(
        dict(
            ar="Accounts receivable",
            cogs="Cost of sales",
            sga="Selling, general and adm.expenses",
        )
    ),
)


def live_balance_sheet():
    ledger = chart.ledger().post_many(st.session_state["entries"])
    report = Report(chart, ledger)
    return report.balance_sheet


st.text(live_balance_sheet())

# TODO-2: текст ниже должен обновляться в момент добавления новых записей через форму
#         сейчас добавляется с задержкой в одну итерацию
#         видимо первая запись - st.session_state["entries"] это дефолтный значения формы с 0,
#         хотя она не нажимаются.
"Введенные через форму проводки (показывает или добавляет с задержкой на одну итерацию):"
st.write(st.session_state["entries"])


# st.write(list(chart.to_dict().keys()))
# with st.form("chart_form"):
#     st.write("Define chart of accounts. Separate account names by space.")
#     assets = st.text_input("Assets", value="cash ar goods")
#     capital = st.text_input("Equity", value="common_stock")
#     liabilities = st.text_input("Liabilities", value="ap")
#     income = st.text_input("Income", value="sales")
#     expenses = st.text_input("Expenses", value="cogs sga")
#     st.form_submit_button("Create chart")

# user_chart = UserChart.default().use(*assets.split(), prefix="asset")
# user_chart.use(*capital.split(), prefix="capital")
# user_chart.use(*liabilities.split(), prefix="liability")
# user_chart.use(*income.split(), prefix="income")
# user_chart.use(*expenses.split(), prefix="expense")
# labels = [
#     n
#     for n in user_chart.names
#     if n
#     not in [
#         chart.income_summary_account,
#         chart.retained_earnings_account,
#         chart.null_account,
#     ]
# ]
# st.write(labels)
