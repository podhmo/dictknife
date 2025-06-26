```markdown
# `dictknife.walkers`

このモジュールは、ネストされた辞書やリストなどのデータ構造を柔軟に探索・走査するためのクラスを提供します。中心となるのは `DictWalker` クラスで、探索条件やコンテキスト、結果の処理方法をカスタマイズできます。

## `DictWalker` クラス

ネストされた辞書やリストを再帰的に探索し、指定された条件 (`qs`) にマッチする要素を見つけ出すためのイテレータを提供します。

**エイリアス:** `LooseDictWalkingIterator` (後方互換性のためのエイリアスです。新しいコードでは `DictWalker` の使用を推奨します。)

### `__init__(self, qs, handler=None, context_factory=None)`

*   `qs`: クエリのシーケンス (リストやタプル)。探索するパスの各階層に対する条件を指定します。
    *   各要素は、リテラル値 (キー名やインデックスと直接比較) や、`dictknife.operators` モジュールで定義された演算子 (`Regexp`, `Any`, `Not`, `Or`, `And` など) のインスタンスです。
    *   例えば、`["users", ANY, "name"]` は、トップレベルの `users` キー -> 任意のキー/インデックス -> `name` キー、というパスを探索します。
*   `handler=None`: マッチした要素が見つかった場合に、その要素をどのように処理するかを定義するハンドラオブジェクト。
    *   デフォルトは `ContainerHandler` インスタンスです。
    *   `DataHandler` やカスタムハンドラを指定できます。
*   `context_factory=None`: 探索中のコンテキスト情報を管理するオブジェクトを生成するファクトリ関数またはクラス。
    *   デフォルトは `PathContext` です。
    *   `SimpleContext`, `RecPathContext` やカスタムコンテキストファクトリを指定できます。

### `walk(self, d, qs=None, depth=-1, ctx=None)`

データ構造 `d` を探索し、条件にマッチした要素をyieldするジェネレータメソッドです。

*   `d`: 探索対象の辞書またはリスト。
*   `qs=None`: `__init__` で指定したものと異なるクエリシーケンスを使用する場合に指定。デフォルトは `__init__` で指定された `qs` を使用。
*   `depth=-1`: 探索する最大の深さ。
    *   `-1` (デフォルト): 深さ制限なし。
    *   `0`: 何も探索しません。
    *   `1`: トップレベルのみ探索。
*   `ctx=None`: `__init__` で指定したものと異なるコンテキストオブジェクトを初期状態で使用する場合に指定。

**戻り値 (yield):**
ハンドラ (`self.handler`) とコンテキスト (`ctx`) の組み合わせによって、yieldされる値の形式が決まります。
デフォルトの `PathContext` と `ContainerHandler` の組み合わせでは、`on_found` メソッドは `ctx(walker, self.handler.identity, d)` を呼び出し、`PathContext` は `fn(self.path, value)` を実行するので、`(path_list, container_dict)` のようなタプルがyieldされることが期待されます。ここで `path_list` はマッチした要素までのパス、`container_dict` はマッチしたキーを含むコンテナです。

**エイリアス:** `iterate` (後方互換性のためのエイリアスです。)

**実行例:**

```python
from dictknife.walkers import DictWalker
from dictknife.operators import ANY, Regexp

data = {
    "users": [
        {"id": 1, "name": "Alice", "settings": {"theme": "dark", "active": True}},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "settings": {"theme": "light", "active": False}},
    ],
    "config": {"version": "1.0", "debug_mode": False}
}

# 例1: 全てのユーザーの名前を取得
# qs: "users" キー -> 任意インデックス -> "name" キー
walker_names = DictWalker(["users", ANY, "name"])
for path, name_value_container in walker_names.walk(data):
    # デフォルトハンドラ(ContainerHandler)はキーを含むコンテナを返す
    # path は ['users', (インデックス), 'name']
    # name_value_container は {'name': 'xxx'} のような辞書
    print(f"Path: {path}, Value: {name_value_container[path[-1]]}")
# 出力例:
# Path: ['users', 0, 'name'], Value: Alice
# Path: ['users', 1, 'name'], Value: Bob
# Path: ['users', 2, 'name'], Value: Charlie

# 例2: 'settings' の中の 'theme' の値を取得 (DataHandlerを使用)
from dictknife.walkers import DataHandler
walker_themes = DictWalker(
    ["users", ANY, "settings", "theme"],
    handler=DataHandler()
)
for path, theme_value in walker_themes.walk(data):
    # DataHandler は実際の値を返す
    # path は ['users', (インデックス), 'settings', 'theme']
    print(f"Path: {path}, Theme: {theme_value}")
# 出力例:
# Path: ['users', 0, 'settings', 'theme'], Theme: dark
# Path: ['users', 2, 'settings', 'theme'], Theme: light

# 例3: 正規表現でキーに 'id' を含むものを探す (深さ制限あり)
walker_ids = DictWalker([Regexp(r"id")], handler=DataHandler())
for path, id_value in walker_ids.walk(data, depth=2): # usersリスト内のidは深さ3なのでマッチしない
    print(f"Path: {path}, ID Value: {id_value}")
# "users" キー自体は depth=1、その中の辞書は depth=2、辞書内の "id" は depth=3
# この例では何も出力されないか、あるいは意図しないトップレベルのキーにマッチする可能性がある。
# クエリを ["users", ANY, Regexp(r"id")] のように具体的にするか、depth調整が必要。

# より正確なID探索の例
walker_user_ids = DictWalker(["users", ANY, "id"], handler=DataHandler())
for path, user_id in walker_user_ids.walk(data):
    print(f"Path: {path}, User ID: {user_id}")
# 出力例:
# Path: ['users', 0, 'id'], User ID: 1
# Path: ['users', 1, 'id'], User ID: 2
# Path: ['users', 2, 'id'], User ID: 3
```

### `on_found(self, ctx, d, k)`

内部メソッド。条件に完全にマッチした際 (`qs` の条件を全て満たしたパスが見つかった時) に呼び出され、`self.handler` を介して結果をyieldします。

### `create_context(self, ctx=None)`

内部メソッド。探索のためのコンテキストオブジェクトを生成または返します。

## コンテキストクラス

探索中に現在のパスや状態を管理します。`DictWalker` の `context_factory` に指定します。

### `SimpleContext`

最も基本的なコンテキスト。パス情報は保持しません。
`__call__(self, walker, fn, value)` は `fn(value)` を呼び出します。

### `PathContext` (デフォルト)

探索中の現在のパス (キー/インデックスのリスト) を `self.path` に保持します。
`__call__(self, walker, fn, value)` は `fn(self.path, value)` を呼び出します。

### `RecPathContext`

`PathContext` を継承。
`__call__(self, walker, fn, value)` は `fn(walker, self.path, value)` を呼び出し、ウォーカー自身も渡します。

## ハンドラクラス

`DictWalker` が条件にマッチする要素を見つけたときに、その要素をどのように処理 (yield) するかを定義します。`DictWalker` の `handler` に指定します。

### `ContainerHandler` (デフォルト)

マッチしたキー `k` を含むコンテナ `d` を、コンテキストを通じて処理します。
デフォルトの `PathContext` と組み合わせると、`(path_to_k, d)` のような形式で結果が渡されることが多いです (実際には `ctx(walker, self.identity, d)` が呼び出され、`PathContext` は `self.identity(path, d)` を呼び、結果として `(path, d)` が返る)。 `d[k]` で実際の値にアクセスできます。

### `DataHandler`

マッチした実際のデータ `d[k]` を、コンテキストを通じて処理します。
デフォルトの `PathContext` と組み合わせると、`(path_to_k, d[k])` のような形式で結果が渡されることが多いです (実際には `ctx(walker, self.identity, d[k])` が呼び出され、`PathContext` は `self.identity(path, d[k])` を呼び、結果として `(path, d[k])` が返る)。

---

**利用上の注意点:**
`DictWalker` の `walk` (または `iterate`) メソッドがyieldする値の具体的な形式は、`context_factory` と `handler` の組み合わせによって変わります。
デフォルトの `PathContext` と `ContainerHandler` の場合、`for path, container in walker.walk(data): ...` のように受け取り、`container[path[-1]]` で値にアクセスできます。
`PathContext` と `DataHandler` の場合は `for path, value in walker.walk(data): ...` のように直接値を受け取れます。
ドキュメントの実行例も参照し、使用するコンテキストとハンドラに応じて適切に結果を処理してください。
```
