import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Accounting as Code",
    page_icon=None,
    layout="centered",
    initial_sidebar_state="collapsed",
)


st.title("Accounding as Code")

"""
A simple balance sheet:

Cash = Equity
"""

balance_str = st.input_text("What is your balance equation?",
                            value = "Cash + Inventory = Equity + Profit")
aktiv, passiv = [item.strip() for item in line.split("+") for line in balance_str.split("=")]
st.write(aktiv)
st.write(passiv)


st.header("Small examples")

"""
Below are some simple examples to get used to [Streamlit][st].

All you do is adding `st.something(x)` to your code 
that will display `x` in the application.
"""


st.subheader("Input and display a number, show code")

with st.echo():
    x = st.number_input("A number please:")
    st.write("Just got", x)

st.subheader("Input and display a number, show code")

color = st.select_slider(
    "Select a color of the rainbow",
    options=["red", "orange", "yellow", "green", "blue", "indigo", "violet"],
)
st.write("My favorite color is", color)


st.subheader("Slider")

hour = st.slider("Hour", 0, 23, 12)

st.subheader("Display text, markdown, latex, variable, code")

st.write("<hr>")
st.text("Fixed width text")
st.markdown("_Markdown_")  # see *
st.latex(r"e^{i\pi} + 1 = 0")
st.write("Most objects")  # df, err, func, keras!
st.write(dict(a=1))
st.write(["st", "is <", 3])  # see *
st.title("My title")
st.header("My header")
st.subheader("My sub")
st.code("for i in range(8): foo()")

st.subheader("Line break")

st.markdown("---")

st.subheader("Graphviz chart")

st.graphviz_chart(
    """
    digraph {
        run -> intr
        intr -> runbl
        runbl -> run
        run -> kernel
        kernel -> zombie
        kernel -> sleep
        kernel -> runmem
        sleep -> swap
        swap -> runswap
        runswap -> new
        runswap -> runmem
        new -> runmem
        sleep -> runmem
    }
"""
)

st.subheader("Checkbox as collapse control")

if st.checkbox("Show raw data"):
    st.subheader("Raw data")

st.subheader("Input text")

with st.echo():
    name = st.text_input("Name")
    st.text(name)

st.subheader("Show dataframe or table")
st.write(
    pd.DataFrame({"first column": [1, 2, 3, 4], "second column": [10, 20, 30, 40]})
)

st.subheader("Now there is a chart")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.line_chart(chart_data)

st.subheader("Now there is a map")
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4], columns=["lat", "lon"]
)
st.map(map_data)