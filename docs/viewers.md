<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `viewers`
Viewers for trial balance, income statement, balance sheet reports. 

**Global Variables**
---------------
- **BOLD**
- **OFFSET**
- **EMPTY**

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `maps`

```python
maps(f, xs)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `red`

```python
red(t: int) → Text
```

Make digit red if negative. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L177"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `bold`

```python
bold(s: Text | str) → Text
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `equalize_length`

```python
equalize_length(p1: PairColumn, p2: PairColumn)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L390"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `print_viewers`

```python
print_viewers(
    rename_dict: dict[str, str],
    tv: TrialBalanceViewer,
    bv: BalanceSheetViewer,
    iv: IncomeStatementViewer
)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TextColumn`
Column for creating tables. Methods to manipulate a column include align and concatenate. 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(strings: list[str]) → None
```






---

#### <kbd>property</kbd> width







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L51"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_right`

```python
add_right(string: str)
```

Add `string` to the right of the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_space`

```python
add_space(n: int = 1)
```

Add `n` spaces to the right of the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L59"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_space_left`

```python
add_space_left(n: int = 1)
```

Add `n` spaces to the left of the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `align`

```python
align(method: str, fill_char: str)
```

Generic method to align all strings in the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `align_center`

```python
align_center()
```

Align all strings to center. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `align_left`

```python
align_left(fill_char=' ')
```

Align all strings to the left. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `align_right`

```python
align_right(fill_char=' ')
```

Align all strings to the right. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `empty`

```python
empty(n: int = 1)
```

Create a new column filled with `n` spaces. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `header`

```python
header(text)
```

Add a header line to the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_bottom`

```python
insert_bottom(text)
```

Insert text at the bottom of the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L74"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_top`

```python
insert_top(text)
```

Insert text at the top of the column. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L67"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `merge`

```python
merge(column)
```

Merge two columns into one. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `refill`

```python
refill(text)
```

Create a new column where all strings are replaced by `text`. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L91"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `String`
String(s: str) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(s: str) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich`

```python
rich()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Number`
Number(n: int) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(n: int) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich`

```python
rich()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Format`
Format() 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```









---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BoldF`
BoldF() 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```









---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `OffsetF`
OffsetF() 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```









---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L132"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Cell`
Cell(content: viewers.String | viewers.Number, formats: list[viewers.Format] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(content: String | Number, formats: list[Format] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rename`

```python
rename(f: Callable)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich`

```python
rich()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `PairColumn`
PairColumn(xs: list[viewers.Cell], ys: list[viewers.Cell]) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(xs: list[Cell], ys: list[Cell]) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L216"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_footer`

```python
add_footer(s: str, n: int)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_empty`

```python
append_empty(n)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L193"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `from_dict`

```python
from_dict(d: dict)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L220"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rename`

```python
rename(rename_dict=None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `text_table`

```python
text_table()
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L237"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Viewer`
Viewer() 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```






---

#### <kbd>property</kbd> width







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width: int | None = None)
```

Rich printing to console. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L247"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich_table`

```python
rich_table(width)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L243"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `text_table`

```python
text_table()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(rename_dict: dict[str, str])
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L267"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `IncomeStatementViewer`
IncomeStatementViewer(statement: abacus.core.IncomeStatement, title: str = 'Income Statement', rename_dict: dict[str, str] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    statement: IncomeStatement,
    title: str = 'Income Statement',
    rename_dict: dict[str, str] = <factory>
) → None
```






---

#### <kbd>property</kbd> pair_column





---

#### <kbd>property</kbd> width







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width: int | None = None)
```

Rich printing to console. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L286"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich_table`

```python
rich_table(width)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L283"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `text_table`

```python
text_table()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L273"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(rename_dict: dict[str, str])
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L296"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BalanceSheetViewer`
BalanceSheetViewer(statement: abacus.core.BalanceSheet, title: str = 'Balance sheet', rename_dict: dict[str, str] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    statement: BalanceSheet,
    title: str = 'Balance sheet',
    rename_dict: dict[str, str] = <factory>
) → None
```






---

#### <kbd>property</kbd> pair_columns





---

#### <kbd>property</kbd> width







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width: int | None = None)
```

Rich printing to console. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L330"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich_table`

```python
rich_table(width=None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L326"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `text_table`

```python
text_table()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L302"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `to_dicts`

```python
to_dicts()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(rename_dict: dict[str, str])
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L342"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `TrialBalanceViewer`
TrialBalanceViewer(statement: dict[str, tuple[int, int]], rename_dict: dict[str, str] = <factory>, headers: tuple[str, str, str] = ('Account', 'Debit', 'Credit'), title: str = 'Trial balance') 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    statement: dict[str, tuple[int, int]],
    rename_dict: dict[str, str] = <factory>,
    headers: tuple[str, str, str] = ('Account', 'Debit', 'Credit'),
    title: str = 'Trial balance'
) → None
```






---

#### <kbd>property</kbd> account_names





---

#### <kbd>property</kbd> credits





---

#### <kbd>property</kbd> debits





---

#### <kbd>property</kbd> width







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L361"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `account_names_column`

```python
account_names_column(header: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L370"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `numeric_column`

```python
numeric_column(values, header)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L251"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `print`

```python
print(width: int | None = None)
```

Rich printing to console. 

---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L380"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rich_table`

```python
rich_table(width=None) → Table
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L373"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `text_table`

```python
text_table() → TextColumn
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/viewers.py#L239"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(rename_dict: dict[str, str])
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
