<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `entries_store`
Write and read accounting entries from a file. 



---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LineJSON`
LineJSON(path: pathlib.Path) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(path: Path) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append`

```python
append(entry: Entry) → None
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_many`

```python
append_many(entries: list[Entry]) → None
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `load`

```python
load(path: Path | str | None = None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `yield_entries`

```python
yield_entries() → Iterable[Entry]
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/entries_store.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `yield_entries_for_income_statement`

```python
yield_entries_for_income_statement(chart: Chart) → Iterable[Entry]
```

Filter entries that will not close income accounts. Used to produce income statement. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
