```markdown
# `dictknife.shape`

このモジュールは、与えられたPythonのデータ構造 (辞書やリスト) を解析し、その「形状」やスキーマの概要を抽出する機能を提供します。具体的には、データ内の各パス、そのパスで見つかる値の型、および代表的なサンプル値をリストアップします。
コマンドラインツール `dictknife shape` のコアロジックでもあります。

## `shape(d, traverse=Traverser().traverse, aggregate=_build_pathlist_from_state, *, squash=False, skiplist=False, separator="/", transform=as_jsonpointer)`

入力データ `d` の形状を解析し、結果を `Row` オブジェクトのリストとして返します。

*   `d`: 解析対象の辞書またはリスト。
*   `traverse` (callable, default: `Traverser().traverse`): データ構造を走査し、パスと値の情報を収集する関数。通常はデフォルトのままで使用します。
*   `aggregate` (callable, default: `_build_pathlist_from_state`): `traverse` によって収集された情報を集約し、最終的な `Row` のリストを生成する関数。通常はデフォルトのままで使用します。
*   `squash` (bool, default: `False`): `True` の場合、入力データがリストで、かつその要素が辞書である場合に、パスの先頭に来るリスト要素を示すマーカー (`[]/`) を除去します。例えば、`[]/person/name` が `person/name` になります。
*   `skiplist` (bool, default: `False`): `True` の場合、パスの末尾がリスト要素マーカー (`[]`) で終わるようなエントリ (例: `person/skills/[]`) を結果から除外します。これはリスト自体ではなく、リストの *要素* の型や例を示します。
*   `separator` (str, default: `/`): 出力されるパス文字列内で、階層を区切るために使用される文字。
*   `transform` (callable, default: `dictknife.langhelpers.as_jsonpointer`): パスの各要素 (キーやリストマーカー) を文字列に変換する際に使用される関数。デフォルトではJSON Pointerの仕様に従い `/` や `~` をエスケープします。

**戻り値:** `Row` namedtuple のリスト。各 `Row` オブジェクトは以下のフィールドを持ちます。
    *   `path` (str): データ構造内の要素へのパス。オプショナルな要素の場合、先頭に `?` が付きます。
    *   `type` (list): そのパスで見つかった値の型 (`type` オブジェクト) のリスト。複数の型が見つかった場合は、それら全てが含まれます (ソート済み)。
    *   `example` (any): そのパスで見つかった値の代表的な例 (最初に見つかった値)。

### `Row` namedtuple

`Row = namedtuple("Row", "path, type, example")` として定義されています。

### 内部クラスと関数

*   `Traverser`: データ構造を再帰的に走査するクラス。
    *   `_State`: `Traverser` が収集した中間情報を保持する内部クラス。
*   `_build_pathlist_from_state`: `_State` オブジェクトから最終的な `Row` リストを構築する関数。

これらの内部コンポーネントは通常、`shape` 関数を通じて間接的に利用されます。

**実行例:**

```python
from dictknife.shape import shape, Row # Row は戻り値の型確認用にインポート
from dictknife.langhelpers import as_jsonpointer # デフォルトの transform 関数

data1 = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "address": {"city": "Tokyo", "zip_code": "100-0000"},
    "tags": ["python", "developer", "data"]
}

shape_info1 = shape(data1)
for row in shape_info1:
    print(f"Path: {row.path}, Types: {[t.__name__ for t in row.type]}, Example: {row.example!r}")
# 出力例 (順不同の可能性あり):
# Path: active, Types: ['bool'], Example: True
# Path: address, Types: ['dict'], Example: {'city': 'Tokyo', 'zip_code': '100-0000'}
# Path: address/city, Types: ['str'], Example: 'Tokyo'
# Path: address/zip_code, Types: ['str'], Example: '100-0000'
# Path: age, Types: ['int'], Example: 30
# Path: name, Types: ['str'], Example: 'Alice'
# Path: tags, Types: ['list'], Example: ['python', 'developer', 'data']
# Path: tags/[], Types: ['str'], Example: 'python'

print("-" * 20)

data2 = [
    {"id": 1, "type": "A", "value": 100, "optional_field": "present"},
    {"id": 2, "type": "B", "value": 200},
    {"id": 3, "type": "A", "value": 150.5, "tags": ["tag1"]},
]

# squash と skiplist の効果を見る
shape_info2_default = shape(data2)
print("--- Default ---")
for row in shape_info2_default:
    print(f"Path: {row.path}, Types: {[t.__name__ for t in row.type]}, Example: {row.example!r}")
# 出力例 (抜粋):
# Path: [], Types: ['dict'], Example: {'id': 1, 'type': 'A', 'value': 100, 'optional_field': 'present'}
# Path: []/id, Types: ['int'], Example: 1
# Path: []/type, Types: ['str'], Example: 'A'
# Path: []/value, Types: ['float', 'int'], Example: 100
# Path: ?[]/optional_field, Types: ['str'], Example: 'present'
# Path: ?[]/tags, Types: ['list'], Example: ['tag1']
# Path: ?[]/tags/[], Types: ['str'], Example: 'tag1'


shape_info2_squashed = shape(data2, squash=True)
print("\n--- Squashed ---")
for row in shape_info2_squashed:
    print(f"Path: {row.path}, Types: {[t.__name__ for t in row.type]}, Example: {row.example!r}")
# 出力例 (抜粋, []/ が除去される):
# Path: id, Types: ['int'], Example: 1
# Path: type, Types: ['str'], Example: 'A'
# Path: value, Types: ['float', 'int'], Example: 100
# Path: ?optional_field, Types: ['str'], Example: 'present'
# Path: ?tags, Types: ['list'], Example: ['tag1']
# Path: ?tags/[], Types: ['str'], Example: 'tag1' (tags自体がオプショナルなので、その子もオプショナル扱いになることがある)


shape_info2_squash_skip = shape(data2, squash=True, skiplist=True)
print("\n--- Squashed & Skiplist ---")
for row in shape_info2_squash_skip:
    print(f"Path: {row.path}, Types: {[t.__name__ for t in row.type]}, Example: {row.example!r}")
# 出力例 (抜粋, tags/[] がなくなる):
# Path: id, Types: ['int'], Example: 1
# Path: type, Types: ['str'], Example: 'A'
# Path: value, Types: ['float', 'int'], Example: 100
# Path: ?optional_field, Types: ['str'], Example: 'present'
# Path: ?tags, Types: ['list'], Example: ['tag1']

# transform を変える例 (JSON Pointerエスケープをしない)
def no_transform(x): return str(x)
data3 = {"foo/bar": 1}
shape_info3_no_transform = shape(data3, transform=no_transform)
print("\n--- No Transform ---")
for row in shape_info3_no_transform:
    print(f"Path: {row.path}")
# 出力: Path: foo/bar

shape_info3_default_transform = shape(data3) # default is as_jsonpointer
print("\n--- Default Transform (as_jsonpointer) ---")
for row in shape_info3_default_transform:
    print(f"Path: {row.path}")
# 出力: Path: foo~1bar
```

このモジュールは、未知のデータ構造の概要を把握したり、複数のデータインスタンスから共通のスキーマを推測したり、あるいは設定ファイルのテンプレートを生成する際などに役立ちます。
```
