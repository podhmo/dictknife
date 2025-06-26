```markdown
# `dictknife.loading.modification`

このパッケージは、`dictknife.loading` のローダー ( `Loader` ) やダンパー ( `Dumper` ) のデフォルトの挙動を動的に変更するためのモジュール群を提供します。各モジュールは `setup(dispatcher)` 関数を公開しており、これを呼び出すことでディスパッチャの特定の動作が変更されます。

通常、これらの modification は `dictknife` のコマンドラインインターフェースで特定のオプションが指定された際に内部的に適用されますが、ライブラリとして `dictknife.loading` を直接利用する際にも個別に適用することが可能です。

## パッケージ内のヘルパー関数

`dictknife.loading.modification` パッケージの `__init__.py` では、以下のヘルパー関数が定義されています。これらは主に各 modification モジュール内部で使用されます。

*   `is_used(dispatcher, name)`: 指定された `name` の modification が既に `dispatcher` に適用済みかどうかを確認します。
*   `use(dispatcher, name)`: 指定された `name` の modification を `dispatcher` に適用済みとして記録します。

## 利用可能な Modification モジュール

### `dictknife.loading.modification.compact`

JSON形式で出力する際に、インデントなしのコンパクトな形式で出力するように変更します。

*   **関数:** `setup(dispatcher)`
*   **対象:** ダンパー (`dispatcher.dumper`)
*   **変更内容:** `dispatcher.dumper.fn_map["json"]` のダンプ関数を、`indent=None` で呼び出すように変更します。

**使用例:**

```python
from dictknife.loading import get_dumper
from dictknife.loading.modification import compact
import sys

dumper = get_dumper("json") # 通常のJSONダンパーを取得
data = {"name": "example", "version": 1, "items": [1, 2, 3]}

print("--- Default JSON dump ---")
dumper.dump(data, sys.stdout)
# 出力例 (インデントあり):
# {
#   "items": [
#     1,
#     2,
#     3
#   ],
#   "name": "example",
#   "version": 1
# }

compact.setup(dumper) # compact modification を適用

print("\n--- Compact JSON dump ---")
dumper.dump(data, sys.stdout)
# 出力例 (インデントなし):
# {"items": [1, 2, 3], "name": "example", "version": 1}
```

### `dictknife.loading.modification.flatten`

データを出力する際に、事前に辞書をフラット化 (ネストした辞書をキーを連結して一段階に展開) するように変更します。

*   **関数:** `setup(dispatcher)`
*   **対象:** ダンパー (`dispatcher.dumper`)
*   **変更内容:** `dispatcher.dumper.fn_map` に登録されている全てのダンプ関数をラップし、ダンプ対象のデータを `dictknife.transform.flatten()` で前処理するようにします。

**使用例:**

```python
from dictknife.loading import get_dumper
from dictknife.loading.modification import flatten
import sys

dumper = get_dumper("json")
data = {"user": {"name": "Alice", "age": 30}, "status": "active"}

print("--- Default JSON dump (nested) ---")
dumper.dump(data, sys.stdout)
# 出力例:
# {
#   "status": "active",
#   "user": {
#     "age": 30,
#     "name": "Alice"
#   }
# }

flatten.setup(dumper) # flatten modification を適用

print("\n--- Flattened JSON dump ---")
dumper.dump(data, sys.stdout)
# 出力例:
# {
#   "status": "active",
#   "user.age": 30,
#   "user.name": "Alice"
# }
```

### `dictknife.loading.modification.unescape_unicode`

入力ストリームからデータを読み込む際に、Unicodeエスケープシーケンス (`\uXXXX` 形式) をデコードするように変更します。

*   **関数:** `setup(dispatcher)`
*   **対象:** ローダー (`dispatcher.loader`)
*   **変更内容:** `dispatcher.loader.fn_map` に登録されている全てのロード関数をラップし、入力ストリームから読み取った文字列に対して `.encode("utf-8").decode("unicode-escape")` を適用し、前後のクォートを除去する前処理を行います。

**使用例:**

```python
from dictknife.loading import get_loader
from dictknife.loading.modification import unescape_unicode
from io import StringIO

loader = get_loader("json") # JSONローダーを取得

# UnicodeエスケープされたJSON文字列
escaped_json_str = '"{\\"name\\": \\"\\u30c6\\u30b9\\u30c8\\u540d\\", \\"value\\": \\"\\u0041\\u0042\\u0043\\"}"' # クォートで囲まれた文字列中のJSON

# modification なしの場合 (入力が文字列リテラルのため、Pythonが先にデコードしてしまう場合があるので注意)
# この例ではStringIOでラップすることで、 modification の効果を明確にする
# loader.load(StringIO(escaped_json_str)) -> 通常はエラーになるか、エスケープされたままの文字列として解釈される

unescape_unicode.setup(loader) # unescape_unicode modification を適用

data = loader.load(StringIO(escaped_json_str))
print(data)
# 出力例:
# {'name': 'テスト名', 'value': 'ABC'}
```
*注意: `unescape_unicode` は入力文字列全体を一度読み込んで処理します。非常に大きなストリームには適さない場合があります。*

### `dictknife.loading.modification.unescape_url`

入力ストリームからデータを読み込む際に、URLエンコード (パーセントエンコーディング) された文字列をデコードするように変更します。

*   **関数:** `setup(dispatcher)`
*   **対象:** ローダー (`dispatcher.loader`)
*   **変更内容:** `dispatcher.loader.fn_map` に登録されている全てのロード関数をラップし、入力ストリームから読み取った文字列に対して `urllib.parse.unquote_plus()` を適用し、前後のクォートを除去する前処理を行います。

**使用例:**

```python
from dictknife.loading import get_loader
from dictknife.loading.modification import unescape_url
from io import StringIO

loader = get_loader("json") # JSONローダーを取得 (他の形式でも動作しうる)

# URLエンコードされたJSON文字列 (実際にはJSONである必要はないが、loaderが対応する形式にデコードされる)
url_encoded_str = '"name=%E3%83%86%E3%82%B9%E3%83%88%20%E5%90%8D&value=A%2BB%20C"' # クォートで囲まれたURLエンコード文字列

# modification なしの場合
# loader.load(StringIO(url_encoded_str)) -> URLエンコードされたままの文字列として解釈される

unescape_url.setup(loader) # unescape_url modification を適用

# この modification は文字列をデコードするだけなので、
# デコード後の文字列がloaderの期待する形式 (この場合はJSON) である必要がある。
# この例では、デコード後がJSONではないため、JSONローダーではエラーになる。
# ここではデコード処理そのものに焦点を当てる。
# 実際の使用では、デコード後の文字列が適切な形式になるようにする。

# 例として、デコード後の文字列を取得する処理をシミュレート
# (実際にはloaderがこの処理を行う)
from urllib.parse import unquote_plus
temp_stream = StringIO(url_encoded_str)
raw_content = temp_stream.read()
if raw_content.startswith('"') and raw_content.endswith('"'): # クォート除去のシミュレーション
    raw_content = raw_content[1:-1]
decoded_string = unquote_plus(raw_content)
print(f"Decoded string: {decoded_string}")
# 出力例:
# Decoded string: name=テスト 名&value=A+B C

# loader に渡すのは、デコード後にJSONとしてパース可能な文字列である必要がある。
# 例えば、URLエンコードされたJSONペイロードの場合:
url_encoded_json = '"%7B%22name%22%3A%20%22%E3%83%86%E3%82%B9%E3%83%88%E5%90%8D%22%2C%20%22value%22%3A%20%22A%2BB%20C%22%7D"'
data = loader.load(StringIO(url_encoded_json))
print(data)
# 出力例:
# {'name': 'テスト名', 'value': 'A+B C'}

```
*注意: `unescape_url` は入力文字列全体を一度読み込んで処理します。非常に大きなストリームには適さない場合があります。*
```
