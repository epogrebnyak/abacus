from abacus.engine.column_builder import Column

col1 = (
    Column(["apples", "oranges", "bananas"])
    .set_title("Fruit sales (by weight)")
    .add_space_left(2)
    .insert_start("Fruit, total")
    .align_left(".")
    .add_right("...")
)
col2 = Column(["1055", "200", "800", "55"])


def test_columns():
    print(col1.header("Items") + col2.header("Sales").align_right().add_space_left(1))
    print(
        col1.markdown_header("Items").markdown_separator().drop_title()
        + col2.markdown_header("Sales")
    )
    assert 1
