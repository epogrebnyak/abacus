from abacus.engine.label_layer import ContraLabel, Prefix, RegularLabel


def test_label_string():
    assert str(RegularLabel(Prefix.ASSET, "cash")) == "asset:cash"
    assert str(ContraLabel("sales", "refunds")) == "contra:sales:refunds"
