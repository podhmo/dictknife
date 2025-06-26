```markdown
# `dictknife.langhelpers`

このモジュールは、`dictknife` ライブラリ全体で利用される可能性のある、さまざまな補助関数やクラスを提供します。文字列操作、プロパティのキャッシュ、JSON Pointerの変換などが含まれます。

## `make_dict`

Pythonのバージョンに応じて、`dict` (Python 3.6以降) または `collections.OrderedDict` (それ以前) を返します。これは、辞書のキーの順序を保持するための互換性レイヤーとして機能します。

**利用例:**

```python
from dictknife.langhelpers import make_dict

# Python 3.6 以降では通常の dict と同様
my_dict = make_dict()
my_dict["b"] = 1
my_dict["a"] = 2
print(list(my_dict.keys())) # 環境により ['b', 'a'] または ['a', 'b'] (3.7+なら挿入順)

# Python 3.5 以前では OrderedDict と同様
# (OrderedDict の場合、キーは挿入順に保持される)
```
*注: この `make_dict` は `dictknife.accessing.Accessor` など、他のモジュールでデフォルトの辞書ファクトリとして内部的に利用されることがあります。*

## `pairsplit(s, sep)`

文字列 `s` を、最初の区切り文字 `sep` で2つの部分に分割します。区切り文字が見つからない場合、2つ目の要素は空文字列になります。

*   `s`: 分割する文字列。
*   `sep`: 区切り文字。

**戻り値:** `(文字列1, 文字列2)` のタプル。

**実行例:**

```python
from dictknife.langhelpers import pairsplit

result1 = pairsplit("key=value", "=")
# result1 is ('key', 'value')

result2 = pairsplit("key:value:another", ":")
# result2 is ('key', 'value:another')

result3 = pairsplit("keyonly", "=")
# result3 is ('keyonly', '')
```

## `pairrsplit(s, sep)`

文字列 `s` を、最後の区切り文字 `sep` で2つの部分に分割します。区切り文字が見つからない場合、2つ目の要素は空文字列になります。`rsplit` の動作に似ています。

*   `s`: 分割する文字列。
*   `sep`: 区切り文字。

**戻り値:** `(文字列1, 文字列2)` のタプル。

**実行例:**

```python
from dictknife.langhelpers import pairrsplit

result1 = pairrsplit("key=value=another", "=")
# result1 is ('key=value', 'another')

result2 = pairrsplit("one:two", ":")
# result2 is ('one', 'two')

result3 = pairrsplit("keyonly", "=")
# result3 is ('keyonly', '')
```

## `reify` クラス

プロパティをキャッシュするためのデコレータクラスです。一度計算されたプロパティの値はインスタンスに保存され、次回以降のアクセスでは再計算せずに保存された値を返します。
これは [pyramid](https://trypyramid.com/) フレームワークから着想を得たものです。

**利用例:**

```python
from dictknife.langhelpers import reify

class MyClass:
    def __init__(self, data):
        self._data = data
        self._compute_count = 0

    @reify
    def expensive_property(self):
        print("Computing expensive_property...")
        self._compute_count += 1
        # 何か重い計算をシミュレート
        return sum(self._data)

obj = MyClass([1, 2, 3, 4, 5])

print(obj.expensive_property)  # "Computing expensive_property..." が出力され、15 が表示される
print(f"Compute count: {obj._compute_count}") # 1

print(obj.expensive_property)  # 計算は行われず、キャッシュされた 15 が表示される
print(f"Compute count: {obj._compute_count}") # 1 (増えない)

# プロパティはインスタンスの属性として保存される
print(obj.__dict__["expensive_property"]) # 15
```

## `as_jsonpointer(k)`

与えられたキー `k` (通常は文字列または整数) をJSON Pointerのフラグメント識別子形式に変換します。具体的には、`~` を `~0` に、`/` を `~1` にエスケープします。

*   `k`: 変換するキー。文字列に変換されて処理されます。

**戻り値:** JSON Pointer形式の文字列。

**実行例:**

```python
from dictknife.langhelpers import as_jsonpointer

ptr1 = as_jsonpointer("foo")
# ptr1 is "foo"

ptr2 = as_jsonpointer("foo/bar")
# ptr2 is "foo~1bar"

ptr3 = as_jsonpointer("foo~bar")
# ptr3 is "foo~0bar"

ptr4 = as_jsonpointer(0) # 数値も扱える
# ptr4 is "0"
```

## `as_path_node(ref)`

JSON Pointerのフラグメント識別子形式の文字列 `ref` を、元のキーの形式に戻します。`as_jsonpointer` の逆操作に相当し、`~1` を `/` に、`~0` を `~` にアンエスケープします。

*   `ref`: JSON Pointer形式の文字列。

**戻り値:** 元のキー形式の文字列。

**実行例:**

```python
from dictknife.langhelpers import as_path_node

node1 = as_path_node("foo")
# node1 is "foo"

node2 = as_path_node("foo~1bar")
# node2 is "foo/bar"

node3 = as_path_node("foo~0bar")
# node3 is "foo~bar"
```
```
