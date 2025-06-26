```markdown
# `dictknife.operators`

このモジュールは、値のフィルタリングや条件評価に使用できる演算子クラスとヘルパー関数を提供します。
主に `dictknife.walkers.DictWalker` などで、探索するキーや値を動的に照合する際に利用されます。

## `apply(q, v, *args)`

条件 `q` を値 `v` (およびオプションの追加引数 `*args`) に適用します。

*   `q`: 適用する条件。
    *   `q` が呼び出し可能 (callable) な場合: `q(v, *args)` を呼び出し、その結果を返します。
    *   `q` が呼び出し可能でない場合: `q == v` の結果を返します。
*   `v`: 条件を適用する対象の値。
*   `*args`: `q` が呼び出し可能な場合に渡される追加の引数。

**戻り値:** 条件の評価結果 (通常は `bool`)。

**実行例:**

```python
from dictknife.operators import apply, Regexp

# q が呼び出し可能でない場合 (単純な比較)
print(apply("hello", "hello")) # True
print(apply("hello", "world")) # False

# q が呼び出し可能な場合 (Regexp オブジェクト)
rx = Regexp(r"he.lo")
print(apply(rx, "hello")) # <re.Match object; span=(0, 5), match='hello'> (True相当)
print(apply(rx, "world")) # None (False相当)

# q が呼び出し可能な場合 (カスタム関数)
def is_even(n):
    return n % 2 == 0
print(apply(is_even, 4)) # True
print(apply(is_even, 3)) # False
```

## `Regexp` クラス

正規表現によるマッチングを行うための演算子です。

### `__init__(self, rx)`

*   `rx`: 正規表現パターン。文字列またはコンパイル済みの正規表現オブジェクト (`re.Pattern`) を指定できます。文字列で渡された場合は内部で `re.compile()` されます。

### `__call__(self, v, *args)`

値 `v` (文字列であると期待される) がコンストラクタで指定された正規表現 `rx` にマッチするかどうかを評価します。`re.search()` を使用するため、文字列の一部にマッチすれば成功とみなされます。

*   `v`: マッチング対象の文字列。
*   `*args`: 無視されます。

**戻り値:** マッチした場合は `re.Match` オブジェクト、マッチしない場合は `None`。

**実行例:**

```python
from dictknife.operators import Regexp, apply
import re

# 文字列で正規表現を指定
op_str = Regexp(r"^[a-zA-Z]+$")
print(bool(apply(op_str, "HelloWorld"))) # True
print(bool(apply(op_str, "HelloWorld123"))) # False

# コンパイル済み正規表現オブジェクトを指定
compiled_rx = re.compile(r"\d{3}-\d{4}")
op_compiled = Regexp(compiled_rx)
print(bool(apply(op_compiled, "123-4567"))) # True
print(bool(apply(op_compiled, "abc-defg"))) # False
```

## `Any` クラス (および `ANY` インスタンス)

常に `True` を返す演算子です。どのような値に対してもマッチします。
シングルトンインスタンス `ANY` が提供されています。

### `__call__(self, v, *args)`

*   `v`: 任意の値。
*   `*args`: 無視されます。

**戻り値:** 常に `True`。

**実行例:**

```python
from dictknife.operators import ANY, apply # または from dictknife.operators import Any; ANY = Any()

print(apply(ANY, "anything"))    # True
print(apply(ANY, None))          # True
print(apply(ANY, 123))           # True
```

## `Not` クラス

指定された条件演算子の結果を否定する演算子です。

### `__init__(self, value)`

*   `value`: 否定する条件。これはリテラル値、または他の演算子インスタンス (`Regexp`, `Any`, `Or`, `And`) などです。

### `__call__(self, v, *args)`

内部で `apply(self.args, v, *args)` を呼び出し、その結果を論理否定 (`not`) して返します。

*   `v`: 評価対象の値。
*   `*args`: 内部の `apply` に渡される追加引数。

**戻り値:** 指定された条件の評価結果の否定 (`bool`)。

**実行例:**

```python
from dictknife.operators import Not, Regexp, apply

# "hello" ではない場合に True
op_not_hello = Not("hello")
print(apply(op_not_hello, "world")) # True
print(apply(op_not_hello, "hello")) # False

# 数字で始まらない場合に True
rx_digits = Regexp(r"^\d")
op_not_starts_with_digit = Not(rx_digits)
print(apply(op_not_starts_with_digit, "abc"))  # True (rx_digits は None を返すので not None は True)
print(apply(op_not_starts_with_digit, "1abc")) # False (rx_digits は Match オブジェクトを返すので not Match は False)
```

## `Or` クラス

複数の条件演算子のうち、いずれか一つでも `True` を返せば `True` を返す演算子 (論理OR)。

### `__init__(self, args)`

*   `args`: 条件のリストまたはタプル。各要素はリテラル値や他の演算子インスタンスです。

### `__call__(self, v, *args)`

`args` 内の各条件 `e` について `apply(e, v, *args)` を順に評価し、最初に `True` となった時点で `True` を返します。全ての条件が `False` の場合は `False` を返します。

*   `v`: 評価対象の値。
*   `*args`: 内部の `apply` に渡される追加引数。

**戻り値:** いずれかの条件が真であれば `True`、そうでなければ `False`。

**実行例:**

```python
from dictknife.operators import Or, Regexp, apply

# "apple", "banana", "cherry" のいずれかであれば True
op_fruits = Or(["apple", "banana", "cherry"])
print(apply(op_fruits, "banana"))  # True
print(apply(op_fruits, "orange"))  # False

# "error" を含むか、全て大文字であれば True
rx_error = Regexp("error")
rx_all_caps = Regexp(r"^[A-Z]+$")
op_or_condition = Or([rx_error, rx_all_caps])
print(apply(op_or_condition, "This is an error message")) # True (rx_error にマッチ)
print(apply(op_or_condition, "WARNING"))                 # True (rx_all_caps にマッチ)
print(apply(op_or_condition, "Normal message"))          # False
```

## `And` クラス

複数の条件演算子のすべてが `True` を返す場合にのみ `True` を返す演算子 (論理AND)。

### `__init__(self, args)`

*   `args`: 条件のリストまたはタプル。各要素はリテラル値や他の演算子インスタンスです。

### `__call__(self, v, *args)`

`args` 内の各条件 `e` について `apply(e, v, *args)` を順に評価し、最初に `False` となった時点で `False` を返します。全ての条件が `True` の場合は `True` を返します。

*   `v`: 評価対象の値。
*   `*args`: 内部の `apply` に渡される追加引数。

**戻り値:** すべての条件が真であれば `True`、そうでなければ `False`。

**実行例:**

```python
from dictknife.operators import And, Not, Regexp, apply

# "admin" であり、かつ "password" ではない場合に True (例: ユーザー名として適切か)
op_user_check = And(["admin", Not("password")]) # "admin" はリテラル値との比較
# この例は意図通りに動かない可能性あり。"admin"という文字列そのものと比較するため。
# 正しくは以下のように Regexp を使うか、あるいは apply の第一引数が評価対象の値と等しいかを期待する。

# "admin" という文字列に一致し、かつ "password" という文字列には一致しない場合
op_user_check_strict = And([Regexp("^admin$"), Not(Regexp("^password$"))])
# apply(op_user_check_strict, "admin") -> True
# apply(op_user_check_strict, "password") -> False
# apply(op_user_check_strict, "user") -> False


# 3文字以上で、かつ全てアルファベットである場合に True
rx_min_len_3 = Regexp(r".{3,}")
rx_alpha_only = Regexp(r"^[a-zA-Z]+$")
op_alpha_3plus = And([rx_min_len_3, rx_alpha_only])

print(apply(op_alpha_3plus, "abc"))    # True
print(apply(op_alpha_3plus, "ab"))     # False (長さが足りない)
print(apply(op_alpha_3plus, "abc1"))   # False (数字が含まれる)
print(apply(op_alpha_3plus, "longerword")) # True

# テストコードで見られた組み合わせ例
# Not("x") AND "xx" AND Not("xxx")
op_complex = And([Not("x"), "xx", Not("xxx")])
print(apply(op_complex, "x"))   # False
print(apply(op_complex, "xx"))  # True
print(apply(op_complex, "xxx")) # False
```
```
