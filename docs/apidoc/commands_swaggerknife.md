```markdown
# `swaggerknife` コマンド

`swaggerknife` コマンドラインツールは、Swagger/OpenAPIドキュメントに特化した高度な操作 (スキーマ変換、マージ、JSONからのスキーマ生成など) を提供します。

## グローバルオプション

*   `--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: ログレベル。
*   `-q, --quiet`: 警告抑制。
*   `--debug`: デバッグモード。

## サブコマンド

### `tojsonschema`

Swagger/OpenAPIドキュメントから特定の定義 (通常は `definitions` または `components/schemas` 内のスキーマ) を抽出し、単一のJSON Schemaファイルとして出力します。

**主なオプション:**

*   `--src <filepath>`: 入力Swagger/OpenAPIファイル。
*   `--dst <filepath>`: 出力JSON Schemaファイル。省略すると標準出力。
*   `--name <definition_name>`: 抽出する定義名 (例: `User`)。この名前のスキーマがルート要素となります。デフォルトは `top`。

**実行例:**

```bash
# openapi.yaml の "User" 定義を user_schema.json として抽出
swaggerknife tojsonschema --src openapi.yaml --name User --dst user_schema.json
```

### `json2swagger`

1つまたは複数のJSONデータファイル (サンプルデータ) から、Swagger/OpenAPIのスキーマ定義 (`definitions` や `components/schemas` に配置される形式) を推測し、生成します。

**主なオプション:**

*   `files`: 入力JSONファイル名のリスト。
*   `--dst <filepath>`: 出力Swagger/OpenAPIファイル。省略すると標準出力。
*   `-o, --output-format <fmt>`: 出力フォーマット (例: `yaml`, `json`)。
*   `--name <schema_name>`: 生成されるメインスキーマ (ルートオブジェクト) の名前。デフォルトは `top`。
*   `--detector <class_name>`: スキーマ構造を検出するためのクラス名。デフォルトは `Detector` (`dictknife.swaggerknife.json2swagger.Detector`)。
*   `--emitter <class_name>`: 検出された情報からスキーマを出力するためのクラス名。デフォルトは `Emitter` (`dictknife.swaggerknife.json2swagger.Emitter`)。
*   `--annotate <filepath>`: スキーマ生成時に追加の情報を付与するためのアノテーションファイル (JSON/YAML形式)。特定のパスに対して型や説明などを手動で指定できます。
*   `--emit {schema,info}`: `schema` (デフォルト) ならSwaggerスキーマを、`info` なら検出された中間情報 (デバッグ用) を出力します。
*   `--with-minimap`: 生成されたスキーマの構造の概要をコメントとして出力します。
*   `--without-example`: 生成されるスキーマから `example` フィールドを除去します。

**実行例:**

```bash
# user_data.json と product_data.json からスキーマを推測し、api_definitions.yaml を生成
swaggerknife json2swagger user_data.json product_data.json --name MainApi --dst api_definitions.yaml -o yaml

# アノテーションファイルを使って詳細情報を追加
swaggerknife json2swagger data.json --annotate annotations.yaml --dst schema_with_details.json
```

### `merge`

複数のSwagger/OpenAPIファイルをマージします。

**主なオプション:**

*   `files`: 入力Swagger/OpenAPIファイル名のリスト。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `--style {ref,whole}`: マージ戦略。デフォルトは `ref`。
    *   `ref`: 各ファイルの定義を `$ref` を使って参照する形でマージします。出力ファイルからの相対パスで参照が記述されます。重複する定義名はエラーになる可能性があります (`--strict`参照)。
    *   `whole`: 全てのファイルをインライン展開して1つの大きなファイルにマージします (`dictknife.deepmerge` の `override=True` に近い挙動)。
*   `--strict`: (`ref` スタイルの場合) マージ時に定義名 (例: `definitions/User`) が衝突した場合にエラーとします。
*   `--wrap <schema_name>`: マージ結果の特定のセクション (デフォルトは `definitions`) の全要素を参照するラッパースキーマを、指定した名前で作成します。これは、マージされた複数のファイルを単一のエンドポイント定義から参照可能にする場合などに使えます。
*   `--wrap-section <section_name>`: `--wrap` オプションが対象とするセクション名。デフォルトは `definitions` (OpenAPI v2)。v3の場合は `components/schemas` などを指定する必要があるかもしれません。

**実行例:**

```bash
# definitions1.yaml と definitions2.yaml を参照形式でマージ
swaggerknife merge definitions1.yaml definitions2.yaml --dst combined_definitions.yaml --style ref

# 全ての .yaml ファイルをインライン展開してマージし、"AllDefinitions" というラッパーでまとめる
swaggerknife merge *.yaml --style whole --wrap AllDefinitions --wrap-section components/schemas -o final_api.yaml
```

### `flatten`

JSON Schema (特にSwagger/OpenAPIドキュメント内の `definitions` または `components/schemas`) のネストしたインライン定義を展開し、トップレベルの定義として「持ち上げ」てフラットな構造にします。元の場所には新しいトップレベル定義への `$ref` が残ります。

**主なオプション:**

*   `src`: 入力ファイル名。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `-i, --input-format <fmt>`, `-o, --output-format <fmt>`, `-f, --format <fmt>`: フォーマット指定。

この機能は `dictknife.jsonknife.lifting.Flattener` を利用して、`definitions` (またはそれに類する) セクション内の各スキーマを処理します。

**実行例:**

```bash
# complex_schema.yaml 内の definitions をフラット化
swaggerknife flatten complex_schema.yaml -o flattened_schema.yaml
```
```
