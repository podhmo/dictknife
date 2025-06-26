```markdown
# `dictknife.jsonknife` (サブモジュール群)

`dictknife.jsonknife` パッケージは、JSON (および互換フォーマット) ドキュメント、特にJSON Reference (`$ref`) を多用するOpenAPI/Swaggerのようなスキーマファイルを扱うためのコア機能を提供するサブモジュール群を含んでいます。`jsonknife` コマンドラインツールはこれらのモジュールを利用しています。

## `accessor.py` - JSON Pointerと参照アクセス

JSON Pointer (RFC6901) を使ったドキュメント内要素へのアクセス、割り当て、削除や、JSON Referenceの解決と連携するアクセサを提供します。

*   **`access_by_json_pointer(doc, query, *, guess=False)`**: `doc` 内の `query` (JSON Pointer) で指定された要素を取得。`guess=True` で数値風文字列キーを整数インデックスとしてフォールバック。
*   **`assign_by_json_pointer(doc, query, value, *, guess=False)`**: `doc` 内の `query` に `value` を割り当て。
*   **`maybe_remove_by_json_pointer(doc, query)`**: `doc` 内の `query` の要素を削除。
*   **`path_to_json_pointer(path_list)`**: キー/インデックスのリストをJSON Pointer文字列に変換。
*   **`json_pointer_to_path(json_pointer_str)`**: JSON Pointer文字列をキー/インデックスのリストに変換。
*   **`StackedAccessor`**: `Resolver` のスタックを管理し、相対的な `$ref` を解決しながらデータにアクセス。
*   **`CachedItemAccessor(StackedAccessor)`**: 解決した `$ref` の結果 (ファイルとデータ) をキャッシュし、再アクセスを高速化。

## `resolver.py` - JSON Referenceの解決

`$ref` (ローカルおよび外部ファイル) を解決し、参照先のデータを取得するリゾルバ。

*   **`OneDocResolver`**: 単一ドキュメント内でのみ `$ref` を解決。外部参照不可。
*   **`ExternalFileResolver`**: 外部ファイルへの `$ref` を解決可能。
    *   ファイルの読み込みとキャッシュ (同じファイルは再読込しない)。
    *   相対パス (`../common.yaml#/definitions/Error`) や絶対パスの参照を解決。
    *   `onload` コールバックでロード後の処理をフック可能。
*   **`get_resolver(filename_or_none, ...)`**: `filename` の有無に応じて適切なリゾルバを返すファクトリ。
*   **`build_subset(resolver, ref_pointer)`**: 指定ポインタから参照される全要素を含む部分ドキュメントを構築。

## `expander.py` - JSON Referenceの展開 (Dereference)

`Resolver` を使用してドキュメント内の `$ref` を再帰的に展開 (インライン化) します。

*   **`Expander` クラス**:
    *   `__init__(resolver)`: `Resolver` インスタンスを取る。
    *   `expand()`: リゾルバのルートドキュメント全体を展開。
    *   `expand_subpart(subpart_data)`: データの一部を展開。
    *   循環参照を検出し、無限ループを防ぐために展開しないようにします (元の `$ref` を残す)。

## `bundler.py` - 分割ドキュメントのバンドル

複数のファイルに分割されたドキュメント群を、`$ref` を解決・正規化しながら単一のドキュメントにまとめます。

*   **`Bundler` クラス**:
    *   `__init__(resolver, strict=False, scanner_factory=None)`
    *   `bundle()`: メイン処理。
        1.  `Scanner` が全参照をスキャンし、外部定義を `item_map` に収集。ローカル参照パスも正規化 (例: `#/definitions/Foo` や `#/components/schemas/Foo`)。
        2.  `LocalrefFixer` がローカル参照名の衝突を回避 (例: ファイル名ベースのプレフィックス付加)。
        3.  `Emitter` が収集・正規化された定義群を単一ドキュメント内に再配置し、全ての `$ref` をバンドル後のローカル参照に書き換える。
*   **`create_scanner_factory_from_flavor(flavor)`**: OpenAPI v2/v3 に応じた `Scanner` 設定を返します。

## `separator.py` - バンドル済みドキュメントの分割

バンドルされた単一ドキュメントを、元のファイル構造や `$ref` パスに基づいて複数のファイルに分割します。

*   **`Separator` クラス**:
    *   `__init__(resolver, format=None, here=None)`
    *   `separate()`: メイン処理。
        1.  `Scanner` がドキュメント内のローカル参照 (`#/definitions/Foo` など) を基に、分割可能な定義とその出力先ファイルパスを特定。
        2.  `Emitter` が特定された各定義を個別のファイルとして書き出し。その際、ファイル内の `$ref` は新しいファイルからの相対パスに修正。
        3.  メインファイルも更新され、分割された定義への `$ref` が新しいファイルパスを指すように変更される。「ツリーシェイキング」により、どこからも参照されなくなった定義はメインファイルから削除されることがある。

## `lifting.py` - スキーマ定義の持ち上げ

ネストしたインラインスキーマ定義 (オブジェクトや配列のアイテム) をトップレベルの `definitions` (または同様のセクション) に「持ち上げ」、元の場所にはそれへの `$ref` を残します。

*   **`Flattener` クラス**:
    *   `extract(schema_data, handler_context)`: スキーマデータを再帰的に処理。
    *   ネストしたオブジェクトや配列の `items` が匿名定義の場合、`Handler` が生成する名前 (例: `ParentNamePropertyName`, `ArrayNameItem`) でトップレベルに抽出し、元の場所を `$ref` で置き換える。
*   **`Handler` クラス**: 処理中のコンテキスト (現在のパス、持ち上げた定義を格納する辞書) を管理。

## `merge.py` - JSON Merge Patch (RFC 7396)

RFC 7396 (JSON Merge Patch) の仕様に基づいて2つのドキュメントをマージします。

*   **`merge(target_doc, patch_doc)`**:
    *   `patch_doc` の値が `null` の場合、`target_doc` から対応するキーを削除。
    *   `patch_doc` の値がオブジェクトの場合、再帰的にマージ。
    *   それ以外の場合 (文字列、数値、配列、`true`, `false`)、`target_doc` の対応する値を `patch_doc` の値で完全に置き換える (配列は要素ごとではなく全体が置換)。

## `patch.py` - JSON Patch (RFC 6902) の生成

2つのドキュメントを比較し、最初のドキュメントを2番目のドキュメントに変換するためのJSON Patch操作 (RFC 6902) のシーケンスを生成します。

*   **`make_jsonpatch(src_doc, dst_doc, *, verbose=False)`**:
    *   `src_doc` から `dst_doc` への変更点を `add`, `remove`, `replace` (現在は `copy`, `move`, `test` は直接生成しない) 操作としてリストで返す。
    *   `verbose=True` で追加のデバッグ情報 (`x-from` など) を付加。
    *   内部で `_Walker` が再帰的に差分を検出し、`_merge` がパスを付加して整形。

## `relpath.py` - 相対パス操作ユーティリティ

ファイルパスや `$ref` 文字列内の相対パスを、基準パスや移動先パスに応じて解決・変換します。

*   **`fixpath(relpath, *, where, to)`**: `where` からの相対パス `relpath` が指す実体を、`to` からの相対パスに変換。
*   **`fixref(ref_str, *, where, to)`**: `$ref` 文字列内のファイルパス部分を `fixpath` で変換。
*   **`relpath(fpath_in_ref, *, where)`**: `$ref` 内のファイルパス `fpath_in_ref` を `where` からの絶対パスに変換。
*   **`normpath(relpath, *, where)`**: `where` からの相対パス `relpath` を正規化された絶対パスに変換。
```
