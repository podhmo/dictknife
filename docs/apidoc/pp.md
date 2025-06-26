```markdown
# `dictknife.pp`

このモジュールは、Pythonのデータ構造 (主に辞書やリスト) を人間が読みやすい形に整形 (pretty print) して出力するためのユーティリティを提供します。

## `pp(d, out=None)`

データ `d` を整形して `out` (デフォルトは標準出力 `sys.stdout`) に出力します。
内部では `json.dump()` を利用しており、以下のデフォルト設定で呼び出されます:
*   `sort_keys=True` (キーでソートされる)
*   `indent=2` (2スペースでインデント)
*   `ensure_ascii=False` (非ASCII文字をそのまま出力)
*   `default=str` (JSONシリアライズ不可能なオブジェクトは `str()` で文字列化)

もし `json.dump()` が `TypeError` (例えば、ソート不可能な型のキーが存在する場合など) を送出した場合、`sort_keys=False` として再度 `json.dump()` を試みます。

*   `d`: 出力するデータ構造。
*   `out`: 出力先のストリームオブジェクト。デフォルトは `sys.stdout`。

**実行例:**

```python
from dictknife.pp import pp
import sys
from io import StringIO

data = {
    "name": "テストユーザー",
    "age": 30,
    "active": True,
    "address": {"city": "東京", "zip": None},
    "tags": ["Python", "dictknife"]
}

# 標準出力へ出力
# pp(data)
# 出力結果 (標準出力に):
# {
#   "active": true,
#   "address": {
#     "city": "東京",
#     "zip": null
#   },
#   "age": 30,
#   "name": "テストユーザー",
#   "tags": [
#     "Python",
#     "dictknife"
#   ]
# }

# StringIO を使って文字列として取得
buffer = StringIO()
pp(data, out=buffer)
output_str = buffer.getvalue()
print(output_str)
# 出力結果 (printによって):
# {
#   "active": true,
#   "address": {
#     "city": "東京",
#     "zip": null
#   },
#   "age": 30,
#   "name": "テストユーザー",
#   "tags": [
#     "Python",
#     "dictknife"
#   ]
# }

# ソート不可能なキーを含む場合のフォールバック (例として)
data_unsortable = {
    1: "one",
    None: "null_key", # 通常、キーにNoneは推奨されないが、TypeErrorの例として
    "b": "bee"
}
# pp(data_unsortable) # Python 3では sort_keys=True でも TypeError にならないことがある
                      # json.dump のデフォルトの挙動に依存
                      # この例では TypeError が発生しにくいが、もし発生した場合は sort_keys=False で試行される
```

## `indent(n, prefix=None, newline=True)`

指定されたインデント `n` (スペース数) を付けて標準出力の内容を整形するためのコンテキストマネージャです。
`with` ブロック内の標準出力 (`sys.stdout`) への書き込みを一時的にキャプチャし、ブロックを抜ける際にキャプチャした内容全体にインデントとオプションのプレフィックスを適用して、元の標準出力へ書き出します。

*   `n`: インデントするスペースの数。
*   `prefix=None`: インデントされたブロック全体の前に挿入する文字列。
*   `newline=True`: `prefix` が指定された場合、`prefix` の後に改行を挿入するかどうか。

**コンテキストマネージャが `yield` する値:**
ブロック内で標準出力の代わりに書き込みに使用できる `io.StringIO` バッファ。ただし、通常はブロック内で普通に `print()` などを使用すれば、それがキャプチャされます。

**実行例:**

```python
from dictknife.pp import indent, pp

data1 = {"id": 1, "value": "first"}
data2 = {"id": 2, "value": "second"}

print("Raw output:")
pp(data1)

print("\nIndented output:")
with indent(4, prefix="-- Start Block --"):
    print("This is the first line inside the block.")
    pp(data1) # ppも標準出力を使うのでインデントされる
    print("And another line.")
    with indent(4, prefix="---- Nested Block ----"): # ネストも可能
        pp(data2)
    print("Back to first level of indent.")
print("-- End Block -- (This line is not indented by the context manager)")

# 出力結果:
# Raw output:
# {
#   "id": 1,
#   "value": "first"
# }
#
# Indented output:
# -- Start Block --
#     This is the first line inside the block.
#     {
#       "id": 1,
#       "value": "first"
#     }
#     And another line.
#     ---- Nested Block ----
#         {
#           "id": 2,
#           "value": "second"
#         }
#     Back to first level of indent.
# -- End Block -- (This line is not indented by the context manager)

# `yield` されるバッファを直接使う例 (あまり一般的ではない)
# with indent(2) as buf:
#     buf.write("Hello from buffer\n")
#     print("Hello from print", file=buf) # このようにバッファを指定する必要がある
```
```
