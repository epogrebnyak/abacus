# Как запустить:
#
# git clone https://github.com/epogrebnyak/abacus.git
# pip install -e .
# streamlit run streamlit_app.py
#
# Что сделать: TODO-1, TODO-2, TODO-3.
#
import streamlit as st

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

if "entries" not in st.session_state:
    st.session_state["entries"] = []


def live_balance_sheet():
    ledger = chart.ledger().post_many(st.session_state["entries"])
    report = Report(chart, ledger)
    return report.balance_sheet


# TODO-1: текст ниже должен обновляться в момент добавления новых записей через форму
#         сейчас добавляется с задержкой в одну итерацию
#         видимо первая запись - st.session_state["entries"] это дефолтный значения формы с 0,
#         хотя она не нажимаются.
st.text(live_balance_sheet())

"Введенные через форму проводки (показывает или добавляет с задержкой на одну итерацию):"
st.write(st.session_state["entries"])


def add_entry(dr, cr, a):
    st.session_state["entries"] += [Entry(dr, cr, a)]


def form_callback(dr, cr, a):
    add_entry(dr, cr, a)
    update_done_posting(dr, cr, a)


def to_int(a):
    try:
        return int(a)
    except ValueError:
        return 0


def update_done_posting(dr, cr, a):
    done_posting.text(f"Posted entry: {dr}, {cr}, {a}")


# st.write(list(chart.to_dict().keys()))

labels = ["cash", "ar", "inventory", "equity", "sales", "cogs", "sga"]
with st.sidebar:
    st.header("Post double entry")
    with st.form("add_entry"):
        dr = st.selectbox("Debit:", labels, index=0)
        cr = st.selectbox("Credit:", labels, index=3)
        a = to_int(st.text_input("Amount (only integer)"))
        st.form_submit_button(
            label="Post entry", on_click=form_callback, args=(dr, cr, a)
        )
        # TODO-2: нужно обновлять подпись ниже после нажатия кнопки формы
        #         (не работает сейчас)
        # TODO-3: эта подпись желательно в формате st.caption "Last posted:""
        done_posting = st.empty()
        st.caption("Last posted:")


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
