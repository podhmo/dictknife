```markdown
# `dictknife.transform`

このモジュールは、辞書やリストのデータ構造を様々な形式に変換したり、特定の条件に基づいて要素を抽出・変更したりするための関数群を提供します。コマンドラインツール `dictknife transform` のコアロジックの一部としても利用されます。

## `flatten(d, *, sep="/")`

ネストされた辞書やリスト `d` を、キーがフラット化された一層の辞書に変換します。
ネストしたキーは `sep` (デフォルトは `/`) で連結されます。リストのインデックスもキーの一部として扱われます。

*   `d`: フラット化する対象の辞書またはリスト。
*   `sep` (str, default: `/`): ネストしたキーを連結する際のセパレータ。

**戻り値:** フラット化された辞書。

**実行例:**

```python
from dictknife.transform import flatten

data = {
    "user": {
        "name": "Alice",
        "age": 30,
        "emails": ["alice@example.com", "personal@example.net"]
    },
    "status": "active"
}

flat_data = flatten(data)
print(flat_data)
# 出力 (キーの順序は不定):
# {
#   'user/name': 'Alice',
#   'user/age': 30,
#   'user/emails/0': 'alice@example.com',
#   'user/emails/1': 'personal@example.net',
#   'status': 'active'
# }

# セパレータを変更
flat_data_dot_sep = flatten(data, sep=".")
print(flat_data_dot_sep)
# 出力 (キーの順序は不定):
# {
#   'user.name': 'Alice',
#   'user.age': 30,
#   'user.emails.0': 'alice@example.com',
#   'user.emails.1': 'personal@example.net',
#   'status': 'active'
# }
```
*注意: 値が単純な非コンテナ型の場合、キーは `None` となり、値はそのまま (ただし文字列の場合はJSON Pointerエスケープされる) になります。例: `flatten("text")` -> `{None: "text"}`*

## `unflatten(d, *, sep="/", accessor=accessing.Accessor())`

`flatten` 関数によってフラット化された辞書 `d` を、元のネストされた構造 (辞書やリスト) に戻します。
キーは `sep` (デフォルトは `/`) を基準に分割され、階層構造が復元されます。数値のみのキーはリストのインデックスとして解釈しようとします。

*   `d`: アンフラット化する対象のフラットな辞書。
*   `sep` (str, default: `/`): キーを分割するためのセパレータ。
*   `accessor` (object, default: `dictknife.accessing.Accessor()` instance): 内部でネスト構造を構築する際に使用するアクセサ。

**戻り値:** ネストされた辞書またはリスト。

**実行例:**

```python
from dictknife.transform import unflatten

flat_data = {
    'user/name': 'Alice',
    'user/age': 30,
    'user/emails/0': 'alice@example.com',
    'user/emails/1': 'personal@example.net',
    'status': 'active'
}

nested_data = unflatten(flat_data)
print(nested_data)
# 出力:
# {
#   'user': {
#     'name': 'Alice',
#     'age': 30,
#     'emails': ['alice@example.com', 'personal@example.net']
#   },
#   'status': 'active'
# }

flat_data_list_only = {
    '0/name': 'item0',
    '1/name': 'item1'
}
nested_list = unflatten(flat_data_list_only)
print(nested_list)
# 出力: [{'name': 'item0'}, {'name': 'item1'}]
```

## `rows(d, *, kname="name", vname="value")`

辞書 `d` を、各キーと値のペアを行オブジェクト (辞書) とするリストに変換します。

*   `d`: 変換対象の辞書。
*   `kname` (str, default: `"name"`): 結果の行オブジェクト内で、元のキーを格納する際のキー名。
*   `vname` (str, default: `"value"`): 結果の行オブジェクト内で、元の値を格納する際のキー名。

**戻り値:** 行オブジェクト (辞書) のリスト。

**実行例:**

```python
from dictknife.transform import rows

data = {"name": "Alice", "age": 30, "city": "Tokyo"}
row_list = rows(data)
print(row_list)
# 出力:
# [
#   {'name': 'name', 'value': 'Alice'},
#   {'name': 'age', 'value': 30},
#   {'name': 'city', 'value': 'Tokyo'}
# ]

row_list_custom_names = rows(data, kname="key", vname="val")
print(row_list_custom_names)
# 出力:
# [
#   {'key': 'name', 'val': 'Alice'},
#   {'key': 'age', 'val': 30},
#   {'key': 'city', 'val': 'Tokyo'}
# ]
```

## `update_keys(d, *, key, coerce=str)`

辞書 `d` (およびネストされた辞書) 内のすべてのキーを、指定された `key` 関数によって変換します。この操作は **破壊的** (元の辞書を変更) です。

*   `d`: キーを変換する対象の辞書。
*   `key` (callable): 各キー (`str` 型に `coerce` された後) を引数に取り、変換後のキー文字列を返す関数。
*   `coerce` (callable, default: `str`): キーを `key` 関数に渡す前に適用する型変換関数。

**戻り値:** キーが変換された元の辞書オブジェクト `d`。

**実行例:**

```python
from dictknife.transform import update_keys
from dictknife.naming import camelcase # dictknife.naming からインポート

data = {"first_name": "Alice", "last_name": "Smith", "contact_info": {"email_address": "alice@example.com"}}

# キーをすべて大文字に変換
update_keys(data.copy(), key=lambda k: k.upper())
# data は変更されるので、コピーに対して操作する例
# print(data) # -> {'FIRST_NAME': 'Alice', 'LAST_NAME': 'Smith', 'CONTACT_INFO': {'EMAIL_ADDRESS': 'alice@example.com'}}

# キーをキャメルケースに変換 (dictknife.namingを利用)
data_for_camel = {"first_name": "Bob", "user_age": 25, "address_details": {"street_name": "Main St"}}
update_keys(data_for_camel, key=camelcase)
print(data_for_camel)
# 出力: {'firstName': 'Bob', 'userAge': 25, 'addressDetails': {'streetName': 'Main St'}}
```

### `update_keys` の派生関数

`update_keys` を `functools.partial` で特殊化した、特定の命名規則にキーを一括変換する便利な関数が提供されています。これらはすべて **破壊的** です。

*   `str_dict(d)`: キーを `str()` で変換 (主に型の一貫性のため)。
*   `normalize_dict(d)`: キーを `dictknife.naming.normalize` で正規化。
*   `snakecase_dict(d)`: キーを `dictknife.naming.snakecase` でスネークケースに変換。
*   `camelcase_dict(d)`: キーを `dictknife.naming.camelcase` でキャメルケースに変換。
*   `kebabcase_dict(d)`: キーを `dictknife.naming.kebabcase` でケバブケースに変換。
*   `pascalcase_dict(d)`: キーを `dictknife.naming.pascalcase` でパスカルケースに変換。

**実行例 (派生関数):**

```python
from dictknife.transform import snakecase_dict, camelcase_dict

data_pascal = {"UserName": "Carol", "EmailAddress": "carol@example.com", "IsActive": True}
snakecase_dict(data_pascal.copy()) # コピーに対して操作
# data_pascal は {'user_name': 'Carol', 'email_address': 'carol@example.com', 'is_active': True} になる

data_snake = {"user_name": "David", "email_address": "david@example.com", "is_active": False}
camelcase_dict(data_snake) # 直接変更
print(data_snake)
# 出力: {'userName': 'David', 'emailAddress': 'david@example.com', 'isActive': False}
```

## `only_num(d)`

辞書 `d` のうち、値が数値 ( `int` または `float`、ただし `bool` は除く) であるか、または数値として解釈できる文字列 (`isdigit()` が `True`) である要素のみを含む新しい辞書を返します。

*   `d`: フィルタリング対象の辞書。

**戻り値:** フィルタリングされた新しい辞書。

**実行例:**

```python
from dictknife.transform import only_num

data = {"name": "Test", "count": 10, "ratio": 0.75, "id_str": "12345", "active": True, "code": "A1"}
numeric_data = only_num(data)
print(numeric_data)
# 出力 (キーの順序は不定):
# {'count': 10, 'ratio': 0.75, 'id_str': '12345'}
```

## `only_str(d)`

辞書 `d` のうち、値が文字列 (`str`) である要素のみを含む新しい辞書を返します。

*   `d`: フィルタリング対象の辞書。

**戻り値:** フィルタリングされた新しい辞書。

**実行例:**

```python
from dictknife.transform import only_str

data = {"name": "Test", "count": 10, "id_str": "12345", "active": True, "code": "A1"}
string_data = only_str(data)
print(string_data)
# 出力 (キーの順序は不定):
# {'name': 'Test', 'id_str': '12345', 'code': 'A1'}
```

## `shrink(d, *, max_length_of_string=100, cont_suffix="...", max_length_of_list=3, with_tail=False, mutable=False)`

データ構造 `d` (辞書やリスト) 内の長い文字列や長いリストを指定された長さに縮小します。ログ出力やデータの概要表示などに便利です。

*   `d`: 縮小対象のデータ構造。
*   `max_length_of_string` (int, default: 100): 文字列の最大長。これを超えた文字列は切り詰められ、`cont_suffix` が付加されます。
*   `cont_suffix` (str, default: `...`): 切り詰められた文字列の末尾に付加される接尾辞。
*   `max_length_of_list` (int, default: 3): リストの最大長。これを超えたリストは先頭からこの長さまで切り詰められます。
*   `with_tail` (bool, default: `False`): `True` の場合、リストが切り詰められる際に、先頭要素だけでなく末尾の要素も `max_length_of_list` 分だけ保持しようとします (現在は実装上、先頭に追加される形になっています)。
*   `mutable` (bool, default: `False`): `True` の場合、元のデータ構造を直接変更 (破壊的変更) します。`False` の場合は新しいデータ構造を返します。

**戻り値:** 縮小されたデータ構造 ( `mutable=False` の場合) または元のデータ構造への参照 ( `mutable=True` の場合)。

**実行例:**

```python
from dictknife.transform import shrink

data = {
    "description": "This is a very long string that definitely exceeds the default maximum length of one hundred characters, so it should be truncated.",
    "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "config": {
        "key": "another long string for testing purposes, let's see if this also gets cut off as expected by the shrink function."
    },
    "empty_list": [],
    "short_string": "Hello"
}

shrunk_data_immutable = shrink(data)
print("--- Immutable Shrink ---")
print(shrunk_data_immutable)
# 出力例 (description と config.key が切り詰められ、items が短縮される):
# {
#   'description': 'This is a very long string that definitely exceeds the default maximum length of one hundred charact...',
#   'items': [1, 2, 3],
#   'config': {
#     'key': "another long string for testing purposes, let's see if this also gets cut off as expected by the sh..."
#   },
#   'empty_list': [],
#   'short_string': 'Hello'
# }

shrunk_data_mutable = data.copy() # 元データを壊さないようにコピー
shrink(shrunk_data_mutable, max_length_of_string=30, max_length_of_list=2, mutable=True)
print("\n--- Mutable Shrink (max_string=30, max_list=2) ---")
print(shrunk_data_mutable)
# 出力例:
# {
#   'description': 'This is a very long string th...',
#   'items': [1, 2],
#   'config': {'key': "another long string for testi..."},
#   'empty_list': [],
#   'short_string': 'Hello'
# }
```
```
