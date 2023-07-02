import sys


def prepend(s):
    if s.startswith("bx"):
        return "call " + s.strip() + " || exit /b"
    return s


gen = sys.stdin.readlines()
print("\n".join(map(prepend, gen)))
