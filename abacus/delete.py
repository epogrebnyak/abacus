doc = """
debit cash credit equity 100
credit cash debit loans 80
credit income debit receivables 8
credit receivables debit cash 5
"""


def to_dict(command_line):
    xs = command_line.split()
    res = dict(value=int(xs[4]))
    res[xs[0]] = xs[1]
    res[xs[2]] = xs[3]
    return {xs[0]: xs[1], xs[2]: xs[3], "value": int(xs[4])}


commands = [to_dict(d) for d in doc.split("\n") if d]
