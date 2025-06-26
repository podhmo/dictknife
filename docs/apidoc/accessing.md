```markdown
# `dictknife.accessing`

このモジュールは、ネストされた辞書やリストへのアクセス、値の割り当て、存在確認などを容易にするためのユーティリティを提供します。

## `Accessor` クラス

辞書やリストへの柔軟なアクセスを提供します。

### `__init__(self, make_dict=make_dict, zero_value=None)`

*   `make_dict`: ネストされた辞書を作成する際のファクトリ関数。デフォルトは `dictknife.langhelpers.make_dict` (通常は `OrderedDict` を返します)。
*   `zero_value`: リストの存在しないインデックスに割り当てる際に、間の要素を埋めるためのデフォルト値。デフォルトは `None`。

### `assign(self, d, path, value)`

辞書 `d` の `path` (キー/インデックスのリスト) で指定された場所に `value` を割り当てます。途中の辞書やリストが存在しない場合は自動的に作成します。

**実行例:**

```python
from dictknife.accessing import Accessor
from dictknife.langhelpers import make_dict

a = Accessor(make_dict=make_dict)
data = make_dict()

# 基本的な割り当て
a.assign(data, ["name"], "Alice")
# data is {'name': 'Alice'}

# ネストした辞書への割り当て
a.assign(data, ["address", "city"], "Tokyo")
# data is {'name': 'Alice', 'address': {'city': 'Tokyo'}}

# リストへの割り当て (インデックスが存在しない場合)
a.assign(data, ["tags", 0], "tag1")
# data is {'name': 'Alice', 'address': {'city': 'Tokyo'}, 'tags': ['tag1']}
a.assign(data, ["tags", 2], "tag3")
# data is {'name': 'Alice', 'address': {'city': 'Tokyo'}, 'tags': ['tag1', None, 'tag3']}

# zero_value を指定した場合
a_custom_zero = Accessor(make_dict=make_dict, zero_value="DEFAULT")
data_custom = make_dict()
a_custom_zero.assign(data_custom, ["values", 2], "val2")
# data_custom is {'values': ['DEFAULT', 'DEFAULT', 'val2']}


# リスト内の辞書への割り当て
a.assign(data, ["items", 0, "id"], 101)
# data is {..., 'items': [{'id': 101}]}
```

### `access(self, d, path)`

辞書 `d` の `path` で指定された値を取得します。パスが存在しない場合は `KeyError` や `IndexError` が発生します。

**実行例:**

```python
val = a.access(data, ["address", "city"])
# val is "Tokyo"

try:
    a.access(data, ["address", "zipcode"])
except KeyError:
    print("zipcode not found")
```

### `maybe_access(self, d, path, *, default=None)`

辞書 `d` の `path` で指定された値を取得します。パスが存在しない場合は `default` 値を返します。

**実行例:**

```python
zipcode = a.maybe_access(data, ["address", "zipcode"], default="N/A")
# zipcode is "N/A"
```

### `exists(self, d, path)`

辞書 `d` の `path` で指定された要素が存在するかどうかを `bool` で返します。

**実行例:**

```python
if a.exists(data, ["items", 0, "id"]):
    print("Item ID exists")
```

### `maybe_remove(self, d, path)`

辞書 `d` の `path` で指定された要素を削除します。要素が存在しない場合は何もしません。

**実行例:**

```python
a.maybe_remove(data, ["tags", 1]) # 'tags' のインデックス1 (None) を削除
# data is {..., 'tags': ['tag1', 'tag3']}
```

## `Scope` クラス

階層的なスコープを持つ設定値へのアクセスを提供します。複数の辞書をスタックとして扱い、値の検索はスタックの上から行われます。

### `__init__(self, init=None, *, accessor=None)`

*   `init`: 初期状態の辞書。
*   `accessor`: 使用する `Accessor` インスタンス。

### `get(self, path, default=None)`

現在のスコープスタックを探索し、`path` に対応する最初の値を取得します。見つからない場合は `default` を返します。

### `push(self, state)` / `pop(self)`

スコープスタックに新しい状態 (辞書) を追加/削除します。

### `scope(self, d=None)`

`with` 文と組み合わせて使用できるコンテキストマネージャ。ブロック内でのみ `d` をスコープスタックに追加します。

**実行例:**

```python
from dictknife.accessing import Scope

base_config = {"color": "blue", "size": 10}
scope = Scope(base_config)

print(scope.get(["color"]))  # "blue"

with scope.scope({"color": "red", "font": "Arial"}):
    print(scope.get(["color"]))  # "red" (現在のスコープから)
    print(scope.get(["size"]))   # 10 (ベーススコープから)
    print(scope.get(["font"]))   # "Arial" (現在のスコープから)

print(scope.get(["color"]))  # "blue" (スコープを抜けたので元に戻る)
```

## `dictmap(fn, x, *, mutable=False, with_key=False)` 関数

辞書やリスト `x` の各要素に再帰的に関数 `fn` を適用します。

*   `fn`: 各要素に適用する関数。
*   `x`: 対象の辞書またはリスト。
*   `mutable=False` (デフォルト): 非破壊的。新しいオブジェクトを返します。`True` にすると元のオブジェクトを変更します。
*   `with_key=False` (デフォルト): `False` なら値のみに `fn` を適用。`True` なら辞書のキーと値の両方に `fn` を適用します。

**実行例:**

```python
from dictknife.accessing import dictmap

data = {"a": 1, "b": {"c": 2, "d": [3, 4]}}

# 値をすべて文字列に変換 (非破壊的)
str_data = dictmap(str, data)
# str_data is {'a': '1', 'b': {'c': '2', 'd': ['3', '4']}}

# 値を2倍にする (破壊的)
def double_if_int(v):
    if isinstance(v, int):
        return v * 2
    return v
dictmap(double_if_int, data, mutable=True)
# data is {'a': 2, 'b': {'c': 4, 'd': [6, 8]}}
```

## `ImmutableModifier` / `MutableModifier` クラス

`dictmap` が内部で使用するクラスで、リストや辞書の再帰的な操作を非破壊的または破壊的に行うためのメソッドを提供します。通常、直接使用する必要はありません。
```
