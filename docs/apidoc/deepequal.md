```markdown
# `dictknife.deepequal`

このモジュールは、ネストされた辞書やリストが、要素の順序が異なっていても意味的に等しいかどうかを比較する機能を提供します。

## `deepequal(d0, d1, normalize=False)`

2つのデータ構造 `d0` と `d1` が深く等しいかどうかを `bool` で返します。

*   `d0`, `d1`: 比較する辞書またはリスト。
*   `normalize=False` (デフォルト):
    *   `False` の場合: 要素の順序を含めて厳密に比較します。リスト内の要素の順序や、辞書のキーの順序 (Python 3.7+では挿入順) が異なれば `False` となります。
    *   `True` の場合: 比較前に内部的に `sort_flexibly` を使ってデータを正規化 (ソート) します。これにより、リスト内の要素の順序や、辞書内のキーの順序が異なっていても、内容が同じであれば等しいと判定されます。

**実行例:**

```python
from dictknife.deepequal import deepequal
from dictknife.langhelpers import make_dict

# normalize=False (デフォルト)
dict1 = {"a": 1, "b": [2, 3]}
dict2 = {"b": [2, 3], "a": 1} # キーの順序が異なる (OrderedDictではない場合)
dict3 = {"a": 1, "b": [3, 2]} # リストの順序が異なる

print(deepequal(dict1, dict1)) # True
# Python 3.7+ の dict は挿入順を保持するため、キーの順序が異なると False になりうる
# ただし、標準の == 演算子はキーの順序を無視するため、この例では True になることが多い
# print(deepequal(dict1, dict2)) # True (dictの==の挙動による)
print(deepequal(dict1, dict3)) # False (リストの順序が異なるため)

# normalize=True
list1 = [{"id": 1}, {"id": 2}]
list2 = [{"id": 2}, {"id": 1}]
print(deepequal(list1, list2, normalize=False)) # False
print(deepequal(list1, list2, normalize=True))  # True

schema1 = {"type": "string", "enum": ["A", "B", "C"]}
schema2 = {"enum": ["C", "A", "B"], "type": "string"}
print(deepequal(schema1, schema2, normalize=False)) # False (キー順序やenumの順序が異なる)
print(deepequal(schema1, schema2, normalize=True))  # True
```

## `sort_flexibly(ob)`

与えられたオブジェクト `ob` (辞書やリスト) を再帰的にソートし、正規化された表現を返します。`deepequal` で `normalize=True` の場合に内部的に使用されます。

この関数は、リスト内の要素をその内容に基づいてソートし、辞書もキーでソートされたかのように扱います。これにより、順序が異なるだけで内容は同じデータ構造が、比較可能になります。

通常、直接この関数を使用する必要はありません。

## `halfequal(left, right)`

`left` の全ての要素が `right` に存在し、かつそれらが再帰的に等しいかどうかを判定します。`deepequal` はこれを双方向で呼び出すことで等価性を担保しています ( `normalize=False` の場合)。

通常、直接この関数を使用する必要はありません。
```
