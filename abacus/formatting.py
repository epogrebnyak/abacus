from itertools import zip_longest


def longest(xs):
    return max(len(x) for x in xs)


def println(strings):
    print(*strings, sep="\n")


def mk_liner(data):
    prepend_words = 2
    longest_words = longest(x[0] for x in data)
    after_words = 3
    prepend_digits = 1
    longest_digits = longest(str(x[1]) for x in data)

    def line(x):
        text, value = x
        return (
            " " * prepend_words
            + text.ljust(longest_words + after_words, ".")
            + " " * prepend_digits
            + str(value).rjust(longest_digits)
        )

    return line


def fmt(data):
    f = mk_liner(data)
    return list((map(f, data)))


def side_by_side(left, right):
    width = longest(left + right)
    gen = zip_longest(left, right, fillvalue="")
    return ["{} {}".format(x.ljust(width, " "), y) for x, y in gen]


data = ("abc", 100), ("defdef", 100000)
assert fmt(data) == ["  abc......    100", "  defdef... 100000"]

data2 = [("eee", 5), ("fff", 10), ("zzzzzzz", 1000)]
assert side_by_side(fmt(data), fmt(data2)) == (
    [
        "  abc......    100   eee.......    5",
        "  defdef... 100000   fff.......   10",
        "                     zzzzzzz... 1000",
    ]
)
println(side_by_side(fmt(data), fmt(data2)))