```markdown
# `dictknife.swaggerknife` (サブモジュール群)

`dictknife.swaggerknife` パッケージは、Swagger/OpenAPIドキュメントの操作に特化した機能を提供するサブモジュール群を含んでいます。`swaggerknife` コマンドラインツールはこれらのモジュールを利用しています。

## `flatten.py` - `definitions` セクションのフラット化

Swagger/OpenAPIドキュメントの `definitions` セクション (または `components/schemas` に相当) 内のネストしたスキーマ定義をフラット化します。

*   **`flatten(data, replace=True)`**:
    *   入力 `data` (Swagger/OpenAPIドキュメント全体) の `definitions` セクションを処理対象とします。
    *   `dictknife.jsonknife.lifting.Flattener` を利用し、各トップレベル定義内のインラインオブジェクトや配列アイテムのスキーマを、新しい名前で `definitions` セクション直下に「持ち上げ」ます。
    *   `replace=True` (デフォルト) の場合、元の場所には持ち上げられた定義への `$ref` が残ります。
    *   結果として、`definitions` セクションがよりフラットで再利用しやすい構造になります。

**注意:** この `flatten` は、OpenAPI v2 の `definitions` を直接参照しています。v3 の `components/schemas` を対象とする場合は、呼び出し側でデータを調整する必要があるかもしれません。

## `json2swagger.py` - JSONデータからのSwagger/OpenAPIスキーマ生成

1つまたは複数のJSONデータサンプルから、Swagger/OpenAPIのスキーマ定義を推測し、生成します。

*   **`Detector` クラス**:
    *   入力JSONデータを再帰的に解析し、各要素の型、出現頻度、子要素の情報などを収集して中間表現 (`info` 辞書) を構築します。
    *   `resolve_type()`: Pythonの型をJSON Schemaの型文字列に変換。
*   **`Emitter` クラス**:
    *   `Detector` が生成した `info` と、オプションの `annotations` (外部からのスキーマへの追加情報) を元に、Swagger/OpenAPIのスキーマ定義 (`definitions` セクションに入る形式) を構築します。
    *   `make_signature()`: `info` からスキーマの構造的シグネチャを生成し、同じ構造のスキーマが同じ定義名で再利用されるようにします (`prestring.NameStore` を利用)。
    *   `make_object_schema()`, `make_array_schema()`, `make_primitive_schema()`: `info` に基づいて各型のスキーマを再帰的に生成し、`definitions` に登録後、それへの `$ref` を返します。
    *   `required` プロパティは出現頻度から推測されます。
    *   `example` は観測された値から設定されます。
*   **アノテーション**: 外部ファイルから特定のパス (`JSON Pointer`風) に対応するスキーマ属性 (例: `description`, `format`, 手動での型指定) を提供することで、生成結果をカスタマイズできます。

## `migration.py` - Swagger/OpenAPIドキュメントのマイグレーションフレームワーク

複数のファイルにまたがる可能性のあるSwagger/OpenAPIドキュメント群に対して、一連の変換処理 (マイグレーション) を行い、その結果を元のファイル構造に書き戻したり、差分を表示したりするための汎用的なフレームワークです。

*   **`Migration` クラス**:
    *   `__init__(resolver, dump_options=None, transform=None)`:
        *   `resolver`: `ExternalFileResolver` を使用し、処理対象の全ファイルにアクセス。
        *   `transform`: (オプション) マイグレーションロジック適用後に、各ドキュメントデータに最終的な変換を施す関数。
    *   `migrate(dry_run=False, inplace=False, savedir=None, ...)`: マイグレーション処理のメインメソッド。
        1.  `_prepare()`: `Bundler` の `Scanner` と同様に、全参照ファイルをスキャンし、`item_map` (処理対象の全定義アイテム) を構築。
        2.  コンテキストマネージャ (`_migrate` または `_migrate_dryrun_and_diff`) が `_Updater` インスタンスを `yield`。
        3.  呼び出し側 (具体的なマイグレーションスクリプト) が `_Updater` を使って `item_map` 内のドキュメントに変更を加える。
        4.  コンテキスト終了後、`_Differ` が変更前後の差分を計算。
            *   `dry_run`: 差分を表示。
            *   実処理: 変更があったファイルを `savedir` (または元の場所へ `inplace`) に書き出す。書き出し前に `transform` 関数が適用される。
*   **`_Updater` クラス**:
    *   ドキュメントの変更操作 (値の更新 `update()`, `update_by_path()` や削除 `pop()`, `pop_by_path()`) を提供。
    *   変更は `ChainMap` や内部的なマーカー (`_Empty`) を使って記録され、元のオブジェクトを直接変更しない形で行われることがあります。
*   **`_Differ` クラス**:
    *   `_Updater` によって加えられた変更の前後の状態を比較し、`dictknife.diff.diff` を使って差分を生成します。

このフレームワーク自体は特定のバージョン移行ロジック (例: OpenAPI v2 to v3) を含んでいませんが、そのようなロジックを実装するための基盤となります。開発者は `_Updater` を使って必要な変更を行い、`Migration` クラスがファイルI/Oや差分表示を処理します。
```
