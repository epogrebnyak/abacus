import sys


def prepend(s):
    if s.startswith("jaba"):
        return "call " + s
    return s


gen = sys.stdin.readlines()
print("".join(map(prepend, gen)))
