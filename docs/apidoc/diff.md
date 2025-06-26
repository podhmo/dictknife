```markdown
# `dictknife.diff`

このパッケージは、2つの辞書やリストの差分を計算し、様々な形式で表示する機能を提供します。

## `diff.py` - Unified Diff形式

### `diff(d0, d1, tostring=None, fromfile="left", tofile="right", n=3, terminator="\n", normalize=False, sort_keys=False)`

2つのデータ構造 `d0` と `d1` の差分を `unified_diff` 形式 (一般的な `diff -u` のような出力) の行イテレータとして返します。

*   `d0`, `d1`: 比較するデータ構造 (辞書、リストなど)。イテレータも可。
*   `tostring=None`: データ構造を文字列に変換する関数。
    *   デフォルト (`None`) の場合、内部で `json.dumps(d, indent=2, ensure_ascii=False, sort_keys=sort_keys, default=str)` を使用して整形されたJSON文字列に変換します。
*   `fromfile="left"`, `tofile="right"`: diff出力のヘッダーに表示されるファイル名。
*   `n=3`: 変更箇所の前後何行のコンテキストを表示するか。
*   `terminator="\n"`: `tostring` で変換された文字列を行に分割する際の区切り文字。
*   `normalize=False`:
    *   `True` の場合、比較前に `dictknife.deepequal.sort_flexibly` を使ってデータを正規化します。これは主にリスト内の要素の順序や辞書のキーの順序が異なる場合に意味のある差分を得るために使われます。
    *   **重要:** `normalize=True` の場合、`sort_flexibly` の処理の一環として、全てのデータ値が `dictknife.transform.str_dict` によって文字列に変換された上で比較されます。そのため、数値やブール値なども文字列として比較される点に注意が必要です。これにより、例えば `1` と `"1"` が異なるものとして扱われる可能性があります (ただし、`sort_flexibly` がこれらを同一視するような正規化を行う場合を除く)。
*   `sort_keys=False`: `tostring` がデフォルトのJSON変換の場合に、JSONのキーをソートするかどうか。`normalize=True` の場合は、`sort_flexibly` によるソートが優先されるため、このオプションの影響は限定的です。

**実行例:**

```python
from dictknife.diff import diff
import datetime

d0 = {"x": datetime.date(2000, 1, 1), "y": {"a": 1, "b": 10}, "z": [1,2,3]}
d1 = {"x": datetime.date(2000, 2, 1), "y": {"a": 1, "c": 10}, "z": [1,3,4]}

for line in diff(d0, d1, fromfile="old.json", tofile="new.json"):
    print(line)

# 出力例:
# --- old.json
# +++ new.json
# @@ -1,10 +1,10 @@
#  {
# -  "x": "2000-01-01",
# -  "y": {
# -    "a": 1,
# -    "b": 10
# -  },
# -  "z": [
# -    1,
# -    2,
# -    3
# -  ]
# +  "x": "2000-02-01",
# +  "y": {
# +    "a": 1,
# +    "c": 10
# +  },
# +  "z": [
# +    1,
# +    3,
# +    4
# +  ]
#  }
```

## `rows.py` - 行ベースの差分表現

### `diff_rows(d0, d1, *, fromfile="left", tofile="right", diff_key="diff", normalize=False)`

2つのデータ構造 `d0` と `d1` の差分を、各要素（プリミティブ値）ごとに行として表現した辞書のリストで返します。これはプログラムで差分を処理しやすい形式です。

*   `d0`, `d1`: 比較するデータ構造。
*   `fromfile="left"`, `tofile="right"`: 結果の辞書内で、`d0` の値と `d1` の値を指すキー名。
*   `diff_key="diff"`: 結果の辞書内で、差分の内容を指すキー名。
*   `normalize=False`: `diff` 関数と同様に、比較前にデータを正規化します。

各行の辞書は以下のキーを持ちます:
*   `"name"`: 要素へのJSON Pointer風のパス (例: `"key1/0/key2"`)。
*   `fromfile` キー (デフォルト `"left"`): `d0` における値。
*   `tofile` キー (デフォルト `"right"`): `d1` における値。
*   `diff_key` キー (デフォルト `"diff"`): 差分の内容。
    *   数値の場合: `d1 - d0` の値。
    *   文字列の場合: `difflib.ndiff` による差分文字列 (例: `"- f- o- o+ b+ a+ r"`)。
    *   変更がない場合: 数値なら `0`、文字列なら空文字列 `""`。
    *   片方にしか存在しない場合: `None`。

**実行例:**

```python
from dictknife.diff.rows import diff_rows
from collections import OrderedDict

left = OrderedDict([
    ("x", 10),
    ("y", "hello"),
    ("nested", OrderedDict([("z", True)])),
    ("items", [10, 20, "apple"])
])
right = OrderedDict([
    ("x", 15),
    ("y", "world"),
    ("nested", OrderedDict([("z", False), ("new", 100)])),
    ("items", [10, 25, "orange"])
])

rows = diff_rows(left, right)
for row in rows:
    print(row)

# 出力例:
# {'name': 'x', 'left': 10, 'right': 15, 'diff': 5}
# {'name': 'y', 'left': 'hello', 'right': 'world', 'diff': '- h- e- l- l- o+ w+ o+ r+ l+ d'} # 文字列差分
# {'name': 'nested/z', 'left': True, 'right': False, 'diff': '- T- r- u- e+ F+ a+ l+ s+ e'} # 真偽値も文字列として比較される
# {'name': 'nested/new', 'left': None, 'right': 100, 'diff': None} # 片方のみ存在
# {'name': 'items/0', 'left': 10, 'right': 10, 'diff': 0} # 数値変更なし
# {'name': 'items/1', 'left': 20, 'right': 25, 'diff': 5} # 数値変更あり
# {'name': 'items/2', 'left': 'apple', 'right': 'orange', 'diff': '- a- p- p- l- e+ o+ r+ a+ n+ g+ e'} # 文字列変更
```

`dictknife diff` コマンドの `--output-format` オプションで `dict`, `md`, `tsv` などを指定した場合、この `diff_rows` の結果が利用されていると考えられます。
```
