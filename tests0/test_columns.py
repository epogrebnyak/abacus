from abacus.engine.column_builder import Column

col1 = (
    Column(["apples", "oranges", "bananas"])
    .add_space_left(2)
    .insert_top("Fruit, total")
    .align_left(".")
    .add_right("...")
    .header("Items")
)
col2 = (
    Column(["1055", "200", "800", "55"]).header("Sales").align_right().add_space_left(1)
)


def test_columns():
    print(col1 + col2)
    assert 1
