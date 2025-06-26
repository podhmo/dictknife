```markdown
# `dictknife.guessing`

このモジュールは、文字列として表現されたデータ (特に辞書やリストの要素) を、その内容に基づいて適切なPythonの型（真偽値、整数、浮動小数点数など）に自動的に変換（推測）する機能を提供します。

CSVファイルや環境変数から読み込んだデータのように、全ての値が最初は文字列として扱われている場合に、それらを構造化データとして扱う前処理として便利です。

## `guess(d, *, guesser_factory=Guesser, default=None, mutable=False)`

メインのインターフェース関数です。与えられたデータ構造 `d` (辞書やリスト) 内の文字列値を再帰的にスキャンし、型推測と変換を試みます。

*   `d`: 型推測を行いたいデータ構造 (辞書やリスト)。
*   `guesser_factory=Guesser`: `Guesser` クラス (または互換性のあるクラス) を指定します。通常は変更する必要はありません。
*   `default=None`: `Guesser` に渡される `default` 関数を指定します。これは、どの型 (bool, int, float) にも一致しない文字列をどのように処理するかを定義します。デフォルトでは、文字列をそのまま返します。
*   `mutable=False` (デフォルト):
    *   `False` の場合: 非破壊的な変換を行います。つまり、元のデータ構造は変更されず、変換後の新しいオブジェクトが返されます。
    *   `True` の場合: 元のデータ構造を直接変更します (破壊的変換)。

**変換ルール:**

1.  入力値がリストや辞書の場合、その要素に対して再帰的に `guess` を呼び出します。
2.  入力値が文字列でない場合、そのまま返します。
3.  入力値が文字列の場合、以下の順で型を推測し、一致すれば対応するPythonの型に変換します:
    *   **真偽値:** `"true"`, `"True"`, `"false"`, `"False"` など (大文字・小文字を区別しない) は `bool` (`True`, `False`) に変換されます。
    *   **整数:** `"-?[1-9]\d*"` または `"0"` に一致する文字列 (例: `"123"`, `"-45"`, `"0"`) は `int` に変換されます。
    *   **浮動小数点数:** `"-?(?:\d*\.\d+(?:e-\d+)?|nan|inf)"` に一致する文字列 (例: `"3.14"`, `".5"`, `"1e-5"`, `"NaN"`, `"Infinity"`, `"-Infinity"`) は `float` に変換されます。`"nan"`, `"inf"` の大文字・小文字は区別される可能性があります (実装依存ですが、多くの場合 `float('nan')`, `float('inf')` になります)。
    *   上記のいずれにも一致しない場合、`default` 関数 (指定されていれば) の結果、または元の文字列がそのまま返されます。

**実行例:**

```python
from dictknife.guessing import guess

data_str = {
    "name": "item",
    "count": "100",
    "price": "25.50",
    "available": "True",
    "discount_rate": "0.1",
    "metadata": {
        "id_str": "007",
        "negative_int": "-5",
        "is_active": "false",
        "not_a_number": "text",
        "infinity_val": "inf",
        "nan_val": "NaN"
    },
    "tags": ["tag1", "123", "False", "0.5"] # リスト内の型変換可能な文字列も対象
}

# 非破壊的変換 (デフォルト)
guessed_data = guess(data_str)
# print(guessed_data)
# {
#   'name': 'item',
#   'count': 100,
#   'price': 25.5,
#   'available': True,
#   'discount_rate': 0.1,
#   'metadata': {
#     'id_str': 7,
#     'negative_int': -5,
#     'is_active': False,
#     'not_a_number': 'text'
#   },
#   'tags': ['tag1', 123, False]
# }

# 元のデータは変更されていない
# print(data_str["count"]) # "100" (文字列のまま)

# 破壊的変換
data_to_mutate = {
    "value_int": "42",
    "value_float": "3.14",
    "value_bool": "false"
}
guess(data_to_mutate, mutable=True)
# print(data_to_mutate)
# {
#   'value_int': 42,
#   'value_float': 3.14,
#   'value_bool': False
# }
# data_to_mutate["value_int"] は 42 (int) に変更されている
```

## `Guesser` クラス

`guess` 関数が内部で使用するクラスです。型判定のための正規表現や再帰的な処理ロジックをカプセル化しています。通常、ユーザーが直接このクラスをインスタンス化する必要はありません。

主なメソッド:
*   `is_bool(self, v)`, `is_int(self, v)`, `is_float(self, v)`: 文字列 `v` がそれぞれの型にマッチするかどうかを判定します。
*   `guess(self, v)`: 実際の型推測と変換ロジック。
```
