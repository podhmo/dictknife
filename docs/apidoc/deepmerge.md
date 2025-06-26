```markdown
# `dictknife.deepmerge`

このモジュールは、複数の辞書やリストを深くマージする機能を提供します。マージの挙動は `method` オプションによって制御できます。

## `deepmerge(*ds, override=False, method="addtoset")`

可変長引数 `*ds` で与えられた複数の辞書 (またはリスト) を順番にマージし、新しいマージ済みのオブジェクトを返します。元のオブジェクトは変更されません。

*   `*ds`: マージする辞書またはリスト。最初の要素がベースとなり、後続の要素が順にマージされます。
*   `override=False` (非推奨): このオプションは非推奨です。`True` に設定すると `method="replace"` と同じ挙動になります。
*   `method="addtoset"` (デフォルト): マージ戦略を指定します。以下のいずれかの文字列を指定できます。

    *   `"addtoset"`:
        *   **辞書の場合:** キーが重複する場合、値を再帰的に `deepmerge` (この場合は `addtoset` 戦略で) します。新しいキーは追加されます。
        *   **リストの場合:** 右側のリストの要素を左側のリストに追加します。ただし、重複する要素は追加しません (集合的な追加)。要素の比較は `in` 演算子で行われます。
    *   `"append"`:
        *   **辞書の場合:** `"addtoset"` と同様です。
        *   **リストの場合:** 右側のリストの要素を左側のリストに単純に追加します (重複を許容)。
    *   `"merge"`:
        *   **辞書の場合:** `"addtoset"` と同様です。
    *   **リストの場合:** `itertools.zip_longest` を使用し、対応するインデックスの要素同士を再帰的に `deepmerge` (この場合は `"merge"` 戦略で) します。
        *   要素がプリミティブ型の場合、右側の要素の値で左側の要素の値を置き換えます。
        *   要素が辞書やリストの場合、さらに再帰的にマージされます。
        *   リストの長さが異なる場合、長い方のリストの残りの要素がそのまま結果に含まれます。
    *   `"replace"`:
        *   **辞書の場合:** キーが重複する場合、右側の値で左側の値を完全に置き換えます (再帰的なマージは行いません)。
        *   **リストの場合:** 右側のリストで左側のリストを完全に置き換えます。

**実行例:**

```python
from dictknife.deepmerge import deepmerge
from dictknife.langhelpers import make_dict # 通常 OrderedDict

d1 = make_dict({"name": "app", "version": "1.0", "settings": {"debug": True, "port": 8000}, "tags": ["web", "api"]})
d2 = make_dict({"version": "1.1", "settings": {"port": 8080, "timeout": 30}, "tags": ["api", "v1"], "new_prop": "hello"})

# method="addtoset" (デフォルト)
merged_addtoset = deepmerge(d1, d2)
# print(merged_addtoset)
# {
#   'name': 'app',
#   'version': '1.1',
#   'settings': {'debug': True, 'port': 8080, 'timeout': 30},
#   'tags': ['web', 'api', 'v1'], # 'api'は重複しない
#   'new_prop': 'hello'
# }

# method="append"
merged_append = deepmerge(d1, d2, method="append")
# print(merged_append)
# {
#   'name': 'app',
#   'version': '1.1',
#   'settings': {'debug': True, 'port': 8080, 'timeout': 30},
#   'tags': ['web', 'api', 'api', 'v1'], # 'api'が重複して追加される
#   'new_prop': 'hello'
# }

# method="replace"
merged_replace = deepmerge(d1, d2, method="replace")
# print(merged_replace)
# {
#   'name': 'app',
#   'version': '1.1',
#   'settings': {'port': 8080, 'timeout': 30}, # settings全体がd2のもので置き換え
#   'tags': ['api', 'v1'], # tags全体がd2のもので置き換え
#   'new_prop': 'hello'
# }


# "merge" メソッドのリストの挙動
list1 = make_dict({"items": [make_dict({"id":1, "val": "a"}), make_dict({"id":2, "val":"b"})]})
list2 = make_dict({"items": [make_dict({"val": "x"}), make_dict({"id":3, "val":"y"}), make_dict({"id":4, "val":"z"})]})

merged_list_merge = deepmerge(list1, list2, method="merge")
# print(merged_list_merge)
# {
#  'items': [
#    {'id': 1, 'val': 'x'}, # id:1, val:a と val:x がマージ (プリミティブは上書き)
#    {'id': 3, 'val': 'y'}, # id:2, val:b と id:3, val:y がマージ (キーがなければ追加、あれば上書き)
#    {'id': 4, 'val': 'z'}  # d2の3番目の要素がそのまま追加
#  ]
# }

# "merge" メソッドのリストの挙動 (プリミティブ要素)
list_prim1 = make_dict({"values": [10, 20, 30]})
list_prim2 = make_dict({"values": [15, 25]})
merged_list_prim = deepmerge(list_prim1, list_prim2, method="merge")
# print(merged_list_prim)
# {
#   'values': [15, 25, 30] # 10->15, 20->25, 30はそのまま
# }

# 複数の辞書をマージ
d3 = make_dict({"settings": {"user": "admin"}, "tags": ["stable"]})
merged_multiple = deepmerge(d1, d2, d3, method="addtoset")
# print(merged_multiple)
# {
#   'name': 'app',
#   'version': '1.1',
#   'settings': {'debug': True, 'port': 8080, 'timeout': 30, 'user': 'admin'},
#   'tags': ['web', 'api', 'v1', 'stable'],
#   'new_prop': 'hello'
# }
```

**注意点:**

*   `deepmerge` は新しい辞書/リストを返します。元のオブジェクトは変更されません。
*   `make_dict` はデフォルトで `dictknife.langhelpers.make_dict` を使用するため、結果の辞書はキーの挿入順を保持する傾向があります (Python 3.7+ の `dict` または `OrderedDict`)。
*   リスト内の要素が辞書の場合、その辞書のマージも指定された `method` に従って再帰的に行われます (ただし、リスト自体が `"replace"` される場合を除く)。
```
