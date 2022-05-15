import re


def no_pars(s):
    return s.replace("(", "").replace(")", "")


def find_at_end(s):
    return re.findall(r"(.+)\s+\[(\w+)\]$", s)[0]


def acronym(s):
    return re.findall(r"\[(\w+)\]", s)[0].lower()


def variable(s: str):
    s = s.strip()
    if not "[" in s:
        short = s.lower()
        long = s
    elif s.endswith("]"):
        long, short = find_at_end(s)
    else:
        short = acronym(s)
        long = s.replace("[", "").replace("]", "")
    return short, long
