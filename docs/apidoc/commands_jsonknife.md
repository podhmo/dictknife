```markdown
# `jsonknife` コマンド

`jsonknife` コマンドラインツールは、JSON (およびYAMLなど `dictknife` が扱える形式) ドキュメント、特にJSON Reference (`$ref`) を含むOpenAPI/Swaggerのようなスキーマファイルを扱うための特化した機能を提供します。

## グローバルオプション

*   `--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: ログレベル。
*   `-q, --quiet`: 警告抑制。
*   `--debug`: デバッグモード。

## サブコマンド

### `cut`

JSONドキュメントから、指定されたJSON Pointerの要素を削除します。

**主なオプション:**

*   `--src <filepath>`: 入力ファイル。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `--ref <JSON Pointer>` (複数指定可): 削除する要素をJSON Pointer (例: `#/definitions/User`, `/paths/~1users/get`) で指定します。

**実行例:**

```bash
# schema.json から definitions/OldApi と paths/~1old~1endpoint を削除
jsonknife cut --src schema.json --ref "#/definitions/OldApi" --ref "/paths/~1old~1endpoint" -o cleaned_schema.json
```

### `select` (旧 `deref`)

JSONドキュメント内のJSON Reference (`$ref`) を解決し、指定された部分または全体を展開 (dereference/expand) して出力します。

**主なオプション:**

*   `--src <filepath_or_uri>`: 入力ファイルまたはURI。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `--ref <JSON Pointer>[@<new_pointer>]` (複数指定可):
    *   展開する対象をJSON Pointerで指定します。
    *   `@<new_pointer>` を付けると、展開結果を指定した新しいJSON Pointerの位置に配置します。省略すると、元の構造に基づいてマージされます。
*   `--unwrap <JSON Pointer>`: 指定したJSON Pointerの部分のみを展開して出力します。`--ref` が指定されていない場合、この値が最初の `--ref` として扱われます。
*   `--wrap <JSON Pointer>`: 展開結果全体を、指定したJSON Pointerの下に配置します。
*   `-f, --format <fmt>`, `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。

**実行例:**

```bash
# openapi.yaml 内の全ての $ref を解決して展開
jsonknife select --src openapi.yaml -o resolved.yaml

# my_schema.json の #/components/schemas/User のみを展開して出力
jsonknife select --src my_schema.json --unwrap "#/components/schemas/User" -o user_schema.json

# external.yaml の内容を、main.yaml の #/definitions/ExternalDef の位置に展開
jsonknife select --src main.yaml --ref "external.yaml@#/definitions/ExternalDef" -o combined.yaml
```
`deref` サブコマンドは非推奨となり、`select` の使用が推奨されます。

### `bundle`

複数のファイルに分割されたJSON/YAMLドキュメント (特にOpenAPI/Swagger) を、JSON Referenceを解決しながら単一のファイルにまとめます。

**主なオプション:**

*   `--src <filepath_or_uri>`: メインとなる入力ファイルまたはURI。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `--ref <JSON Pointer>`: `--src` ファイル内の特定のJSON Pointerを開始点としてバンドルします (例: `src.yaml#/components/schemas/User`)。
*   `--flavor {openapiv3,openapiv2}`: OpenAPIのバージョン。デフォルトは `openapiv3`。ローカル参照のデフォルト位置 (`components/schemas` vs `definitions`) などに影響します。
*   `--extra <filepath>` (複数指定可): バンドルプロセスに追加で読み込ませる外部ファイル。メインファイルから直接参照されていなくてもバンドルに含めたい定義などを指定できます。
*   `-f, --format <fmt>`, `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。

**実行例:**

```bash
# main.yaml とそれが参照する ./schemas/*.yaml をバンドルして単一の openapi_bundled.yaml を作成
jsonknife bundle --src main.yaml -o openapi_bundled.yaml

# OpenAPI v2 形式でバンドル
jsonknife bundle --src swagger.yaml --flavor openapiv2 -o swagger_bundled.yaml
```

### `separate`

バンドルされた単一のJSON/YAMLドキュメントを、元のファイル構造 (`x-original-$ref`などの情報や参照パスに基づいて) に分割して複数のファイルとして出力します。

**主なオプション:**

*   `--src <filepath>`: バンドルされた入力ファイル。
*   `--dst <directory_path>`: 分割されたファイルを出力するディレクトリ。省略するとカレントディレクトリ。
*   `-f, --format <fmt>`, `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。出力フォーマットは分割される各ファイルに適用されます。

**実行例:**

```bash
# bundled_openapi.yaml を ./separated_components ディレクトリに分割
jsonknife separate --src bundled_openapi.yaml --dst ./separated_components --output-format yaml
```

### `examples`

OpenAPI/Swaggerスキーマからサンプル値を生成して出力します。

**主なオプション:**

*   `src <filepath_or_uri>`: 入力となるスキーマファイルまたはURI。
*   `--dst <filepath>`: 出力ファイル。省略すると標準出力。
*   `--ref <JSON Pointer>`: スキーマ内の特定の箇所 (例: `#/components/schemas/User`) からサンプル値を生成します。`src` に `#/foo` が含まれる場合はそれが優先されます。
*   `--limit <int>`: 配列のサンプル値を生成する際の最大要素数。デフォルトは5。
*   `--expand`: サンプル生成前に、入力スキーマの `$ref` をバンドル・展開します。複雑な参照を持つスキーマで有用です。
*   `-f, --format <fmt>`, `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。出力は通常JSON。

**実行例:**

```bash
# api.yaml の User スキーマからサンプルJSONを生成
jsonknife examples api.yaml --ref "#/components/schemas/User" -o user_example.json

# 参照を解決してからサンプルを生成
jsonknife examples api_with_refs.yaml --expand --ref "#/components/schemas/ComplexObject"
```
```
