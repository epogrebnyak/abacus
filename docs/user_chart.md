<!-- markdownlint-disable -->

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `user_chart`
User-defined chart of accounts. 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `extract`

```python
extract(
    input_string: str,
    composer: Composer | None = None
) → Union[Iterable[Label], Iterable[Offset]]
```

Extract one or several account labels from an input string. 

Input string examples: 


- "asset:cash" 
- "asset:cash,ap,inventory" 
- "income:sales" 
- "contra:sales:refunds" 
- "contra:sales:refunds,voids" 


---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `make_user_chart`

```python
make_user_chart(*args)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L12"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `AccountLabel`
AccountLabel(type: abacus.core.T, contra_names: list[str] = <factory>) 

### <kbd>function</kbd> `__init__`

```python
__init__(type: T, contra_names: list[str] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L17"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `offset`

```python
offset(name)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Label`
Label(t: abacus.core.T, name: str) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(t: T, name: str) → None
```









---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Offset`
Offset(name: str, contra_name: str) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: str, contra_name: str) → None
```









---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Composer`
Composer(contra: str = 'contra', translation: dict[str, str] = <factory>) 

<a href="https://github.com/rustedpy/result/blob/master/<string>"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(contra: str = 'contra', translation: dict[str, str] = <factory>) → None
```








---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add`

```python
add(t: T, alt_prefix: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L46"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `extract`

```python
extract(input_string: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `select`

```python
select(incoming_prefix: str)
```






---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L78"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `UserChart`





---

#### <kbd>property</kbd> names







---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L172"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `accounts`

```python
accounts(t: T)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L157"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_many`

```python
add_many(t: T, names: list[str])
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_one`

```python
add_one(obj: Label | Offset)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L119"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `assert_unique`

```python
assert_unique(name)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `chart`

```python
chart()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L208"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `default`

```python
default()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L86"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `default_user_chart`

```python
default_user_chart()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `last`

```python
last(name: str) → str
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L201"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `load`

```python
load(path: Path | str | None = None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `name`

```python
name(name: str, title: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `offset`

```python
offset(name: str, contra_name: str)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save()
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_isa`

```python
set_isa(name)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_null`

```python
set_null(name)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L191"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_path`

```python
set_path(path: Path | None = None)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L164"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_re`

```python
set_re(name)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L140"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `use`

```python
use(
    *label_strings: str,
    prefix: str | None = None,
    composer: Composer | None = None
)
```





---

<a href="https://github.com/rustedpy/result/blob/master/abacus/user_chart.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `yield_names`

```python
yield_names()
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
