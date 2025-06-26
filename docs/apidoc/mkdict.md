```markdown
# `dictknife.mkdict`

このモジュールは、特定のミニ言語構文で記述された一行の文字列から、Pythonの辞書または辞書のリストを生成する機能を提供します。コマンドラインツール `dictknife mkdict` のコアロジックでもあります。

## `mkdict(line, *, separator="/", delimiter=";", accessor=_AccessorSupportList(make_dict), guess=guess, shared=None)`

与えられた文字列 `line` を解析し、辞書または辞書のリストを構築して返します。

*   `line` (str): 解析対象の文字列。独自のミニ言語構文で記述されます。
*   `separator` (str, default: `/`): ネストされたキーを指定する際の区切り文字。例えば `parent/child` は `{"parent": {"child": ...}}` のように解釈されます。
*   `delimiter` (str, default: `;`): 複数の辞書エントリを区切るための文字。この文字で区切られた場合、結果は辞書のリストになります。
*   `accessor` (object, default: `_AccessorSupportList` instance): 内部的にキーと値の割り当てを行うアクセサオブジェクト。デフォルトの `_AccessorSupportList` は、パスの指定に応じてリストも適切に扱えるように拡張されたアクセサです。
*   `guess` (callable, default: `dictknife.guessing.guess`): 値の型を推論する関数。文字列 "true", "false", "null", "10", "3.14" などが適切なPythonの型 (bool, None, int, float) に変換されます。
*   `shared` (dict, default: `None`): 複数の `mkdict` 呼び出しや、内部のブロック間で共有される変数を格納するための辞書。`None` の場合は呼び出しごとに独立した変空間が使われます。

**戻り値:** 生成された辞書、または辞書のリスト。

### ミニ言語の主要構文

`mkdict` が解釈する文字列 `line` は、以下のルールに基づいた構文を持ちます。

1.  **キーと値のペア:**
    スペース区切りで `キー 値` のように指定します。
    例: `name Alice age 30` -> `{'name': 'Alice', 'age': 30}`

2.  **ネストしたキー (separator):**
    `separator` (デフォルト `/`) を使ってキーをネストできます。
    例: `user/name Alice user/contact/email alice@example.com`
    -> `{'user': {'name': 'Alice', 'contact': {'email': 'alice@example.com'}}}`

3.  **複数の辞書 (delimiter):**
    `delimiter` (デフォルト `;`) を使うと、複数の辞書からなるリストを生成できます。
    例: `id 1 ; id 2` -> `[{'id': 1}, {'id': 2}]`

4.  **値のグループ化 (ブロック `{}`):**
    `{` と `}` で囲むことで、値をグループ化できます。これは主にネストした辞書を値として割り当てる際に使います。
    例: `user { name Alice age 30 } status active`
    -> `{'user': {'name': 'Alice', 'age': 30}, 'status': 'active'}`

5.  **変数定義 (`@`):**
    `@変数名 値` または `@変数名/ネストキー 値` で変数を定義できます。変数は内部の共有空間 (`shared` または `variables`) に保存されます。
    例: `@default_user { name Unknown active false }`

6.  **変数参照 (`&`):**
    `&変数名` または `&変数名/ネストキー` で定義済みの変数を参照できます。
    例: `user1 &default_user user2 { name Alice }` (user2 は default_user を部分的に上書き)

7.  **リストの作成:**
    キーの末尾に `separator` を付ける (例: `items/`) か、パスの途中で空のキー (`//`) や数値インデックスを指定することでリストやリスト内の要素を操作できます。
    *   `items/ value1 items/ value2` -> `{'items': ['value1', 'value2']}`
    *   `items//name valueA items//name valueB` -> `{'items': [{'name': 'valueA'}, {'name': 'valueB'}]}`
    *   `items/0/name valueA items/1/name valueB` -> `{'items': [{'name': 'valueA'}, {'name': 'valueB'}]}`
    *   `items/-1/property value` は、現在のリストの最後の要素に `property` を追加/更新します。

8.  **エスケープ:**
    `{{`, `}}`, `&&`, `@@` はそれぞれ `{`, `}`, `&`, `@` という文字そのものとして扱われます。

9.  **値の型推論:**
    値は `guess` 関数によって型が推論されます。
    `"true"` -> `True`, `"10"` -> `10`, `"3.14"` -> `3.14`, `"null"` -> `None`。

**実行例:**

```python
from dictknife.mkdict import mkdict
from dictknife.langhelpers import make_dict # OrderedDictのため (Python 3.6+では不要かも)
from dictknife.guessing import guess as default_guess
from dictknife.mkdict import _AccessorSupportList

# カスタムアクセサやguess関数も指定可能だが、通常はデフォルトで十分
custom_accessor = _AccessorSupportList(make_dict=make_dict)

# 基本的な例
data1 = mkdict("name Alice age 30 active true")
print(data1)
# 出力: {'name': 'Alice', 'age': 30, 'active': True}

# ネストとリスト
data2 = mkdict("user/name Bob user/tags/ tag1 user/tags/ tag2 score 100.5")
print(data2)
# 出力: {'user': {'name': 'Bob', 'tags': ['tag1', 'tag2']}, 'score': 100.5}

# デリミタを使ったリスト
data3 = mkdict("type A value 1 ; type B value 2 ; type C value 3")
print(data3)
# 出力: [{'type': 'A', 'value': 1}, {'type': 'B', 'value': 2}, {'type': 'C', 'value': 3}]

# ブロックと変数
line4 = "@common_settings { debug false port 8080 } server1 { host localhost } server1/settings &common_settings ; server2 { host 192.168.1.100 } server2/settings &common_settings server2/settings/port 9000"
data4 = mkdict(line4)
print(data4)
# 出力:
# [
#   {'server1': {'host': 'localhost', 'settings': {'debug': False, 'port': 8080}}},
#   {'server2': {'host': '192.168.1.100', 'settings': {'debug': False, 'port': 9000}}}
# ]

# 共有変数を使った例
shared_vars = {}
mkdict("@shared_val initial", shared=shared_vars)
data5_part1 = mkdict("item1 &shared_val", shared=shared_vars)
mkdict("@shared_val updated", shared=shared_vars) # shared_vars内の値を更新
data5_part2 = mkdict("item2 &shared_val", shared=shared_vars)

print(f"Shared vars: {shared_vars}")
print(f"Data5 Part1: {data5_part1}")
print(f"Data5 Part2: {data5_part2}")
# 出力:
# Shared vars: {'shared_val': 'updated'}
# Data5 Part1: {'item1': 'initial'}
# Data5 Part2: {'item2': 'updated'}

# リスト内の要素への詳細なアクセス
line6 = "items//id 1 items/-1/name A items//id 2 items/-1/name B items/0/status active"
data6 = mkdict(line6)
print(data6)
# 出力: {'items': [{'id': 1, 'name': 'A', 'status': 'active'}, {'id': 2, 'name': 'B'}]}
```

### 内部関数とクラス

*   `_mkdict(...)`: `mkdict` のコアロジックを実装する再帰関数。
*   `tokenize(line)`: `shlex` をベースにしたカスタムトークナイザ。入力行をミニ言語のトークンに分割します。
*   `_AccessorSupportList`: `dictknife.accessing.Accessor` を継承し、リストのインデックス (`/0/`, `//`, `/-1/`) を特別扱いしてリスト操作をサポートする内部クラス。

これらの内部コンポーネントは通常、`mkdict` 関数を通じて間接的に利用されます。
```
