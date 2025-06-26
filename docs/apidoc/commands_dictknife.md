```markdown
# `dictknife` コマンド

`dictknife` コマンドラインツールは、JSON、YAML、TOMLなどの構造化データを扱うための多機能ツールです。データのマージ、変換、差分表示、構造解析など、様々な操作を行えます。

## グローバルオプション

これらのオプションは、全てのサブコマンドに共通して (または多くの場合に) 利用可能です。

*   `--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}`: ログレベルを設定します。デフォルトは `INFO`。
*   `-q, --quiet`: 警告を抑制し、ログレベルを `WARNING` にします。
*   `--debug`: デバッグモード。エラー発生時に簡潔なトレースバックを表示します。
*   `--compact`: (主にJSON出力時) インデントなしのコンパクトな形式で出力します。
*   `--flatten`: データをフラット化します (詳細は `dictknife.loading.modification.flatten` を参照)。ロード時に適用されます。
*   `--unescape {unicode,url}`: Unicodeエスケープシーケンス (`\uXXXX`) やURLエンコードされた文字列をデコードします。ロード時に適用されます。

## サブコマンド

### `cat`

複数のファイルを読み込み、マージして単一のドキュメントとして出力します。

**主なオプション:**

*   `files`: 入力ファイル名のリスト。省略すると標準入力から読み込みます。
*   `--dst <filepath>`: 出力ファイルパス。省略すると標準出力。
*   `-f, --format <fmt>`: 入出力のデフォルトフォーマット (例: `json`, `yaml`, `toml`)。
*   `-i, --input-format <fmt>`: 入力フォーマットを明示的に指定。
*   `-o, --output-format <fmt>`: 出力フォーマットを明示的に指定。
*   `--slurp`: 各入力ファイルを1行ずつ読み込み、それぞれを個別のドキュメントとして扱ってマージします (主にJSON Lines形式などで使用)。
*   `--size <int>`: 各ファイルから読み込むドキュメント数を制限します (`--slurp` と併用)。
*   `--encoding <enc>`: 入力ファイルのエンコーディング。
*   `--errors <handler>`: エンコーディングエラーの処理方法 (`strict`, `ignore` など)。
*   `-S, --sort-keys`: 出力時にキーをソートします (主にJSONやYAML出力時)。
*   `--merge-method {addtoset,append,merge,replace}`: 複数の入力ファイルをマージする際の戦略。デフォルトは `addtoset`。詳細は `dictknife.deepmerge` を参照。
*   フォーマット固有オプション: (例: `--yaml-default-flow-style`) `dictknife.cliutils.extraarguments` を通じて、選択されたフォーマットに応じた追加オプションが利用可能です。

**実行例:**

```bash
# config1.yml と config2.json をマージして result.json に出力
dictknife cat config1.yml config2.json -o result.json --output-format json

# 標準入力からYAMLを読み込み、キーをソートしてJSONで標準出力
cat data.yaml | dictknife cat -f yaml -o - --output-format json -S
```

### `transform`

入力データに対してPythonコードや定義済みの変換関数を適用し、結果を出力します。

**主なオプション:**

*   `src`: 入力ファイル名。省略すると標準入力。
*   `--dst <filepath>`: 出力ファイルパス。省略すると標準出力。
*   `--code <python_expr>`: データ `d` を引数とするPythonの式 (ラムダ式など) で変換処理を定義。例: `--code "lambda d: {k.upper(): v for k, v in d.items()}"`
*   `--fn <name_or_path>`, `--function <name_or_path>` (複数指定可):
    *   `dictknife.transform` モジュール内の関数名 (例: `flatten`, `squash_keys`)。
    *   または `<module>:<function_name>` 形式 (例: `my_transforms:custom_func`)。
    *   複数指定した場合、順番に適用されます。
*   `-i, --input-format <fmt>`, `-o, --output-format <fmt>`, `-f, --format <fmt>`: フォーマット指定。
*   `-S, --sort-keys`: 出力時のキーソート。

**実行例:**

```bash
# data.json の全キーを大文字に変換
dictknife transform data.json --code "lambda d: {k.upper(): v for k, v in d.items()}"

# data.yaml の値を全て文字列に変換し、その後キーをフラット化
dictknife transform data.yaml --fn "lambda d: dictmap(str, d)" --fn flatten -o flattened_data.json
```

### `diff`

2つのファイルの内容を比較し、差分を表示します。

**主なオプション:**

*   `left`: 比較対象の左側のファイル。
*   `right`: 比較対象の右側のファイル。
*   `--normalize`: 比較前にデータを正規化 (順序不問の比較)。詳細は `dictknife.deepequal.sort_flexibly` を参照。
*   `--n <int>`: (unified diff形式の場合) 変更箇所の前後コンテキスト行数。デフォルトは3。
*   `--skip-empty`: (`dict`, `md`などの行ベース出力時) 差分のない行をスキップします。
*   `-i, --input-format <fmt>`: 入力フォーマット。
*   `-o, --output-format {diff,dict,md,tsv,jsonpatch,pair}`: 出力フォーマット。
    *   `diff` (デフォルト): 標準的なunified diff形式。
    *   `jsonpatch`: RFC6902 JSON Patch形式。
    *   `pair`: 左右のファイルを整形して並べて表示。
    *   その他 (`dict`, `md`, `tsv`): `dictknife.diff.rows` による行ごとの差分情報。
*   `-S, --sort-keys`: (主に `pair` や `jsonpatch` の内部JSON変換時) キーをソート。
*   `--verbose`: (`jsonpatch` 出力時) 詳細な差分情報を追加。

**実行例:**

```bash
# file1.json と file2.json の差分をunified diffで表示
dictknife diff file1.json file2.json

# file1.yaml と file2.yaml の差分をJSON Patch形式で表示 (正規化あり)
dictknife diff file1.yaml file2.yaml --normalize -o jsonpatch
```

### `shape`

入力データの構造 (キーのパス、型、具体例など) を解析し、表示します。スキーマの自動生成やデータ理解に役立ちます。

**主なオプション:**

*   `files`: 入力ファイル名のリスト。省略すると標準入力。
*   `--squash`: 複数の入力ファイルを1つのデータセットとして扱って解析します。
*   `--skiplist`: リストの要素を個別に解析せず、リスト自体を1つの型として扱います。
*   `--full`: 例 (example) を省略せずに表示します (通常は大きなリストや辞書は省略される)。
*   `--with-type`: 型情報を表示します。
*   `--with-example`: 具体例を表示します。
*   `--separator <char>`: 出力されるパスの区切り文字。デフォルトは `/`。
*   `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。出力フォーマットを指定しない場合はプレーンテキストで標準出力。

**実行例:**

```bash
# data.json の構造を解析し、型と例を表示
dictknife shape data.json --with-type --with-example -o shape_summary.csv --output-format csv
```

### `shrink`

大きなデータ構造 (長い文字列や多数の要素を持つリスト) を、指定された長さに縮小して表示します。巨大なデータの概要を把握するのに便利です。

**主なオプション:**

*   `files`: 入力ファイル名のリスト。省略すると標準入力。
*   `--max-length-of-string <int>`: 文字列の最大表示長。デフォルトは100。
*   `--max-length-of-list <int>`: リストの最大表示要素数。デフォルトは3。
*   `--cont-suffix <str>`: 省略時に付加する接尾辞。デフォルトは `...`。
*   `--with-tail`: リストを省略する際に、先頭要素だけでなく末尾の要素も表示します。
*   `-i, --input-format <fmt>`, `-o, --output-format <fmt>`: フォーマット指定。

**実行例:**

```bash
# large_data.json の文字列を20文字、リストを2要素に縮小して表示
dictknife shrink large_data.json --max-length-of-string 20 --max-length-of-list 2 -o shrunk_data.json
```

### `mkdict`

シンプルなキーバリュー形式のテキスト (標準入力またはコマンドライン引数) から辞書を生成します。

**主なオプション:**

*   入力は標準入力から1行1定義、またはコマンドライン引数の末尾に `key=value` や `key/subkey=value` の形式で与えます。
*   `--squash`: 各入力行から生成された辞書を、個別のドキュメントとして出力します (JSON Linesのような形式)。
*   `-o, --output-format <fmt>`: 出力フォーマット。デフォルトは `json`。
*   `--separator <char>`: ネストしたキーの区切り文字。デフォルトは `/` (例: `path/to/key=value`)。
*   `--delimiter <char>`: (現在明確な用途不明)
*   `-S, --sort-keys`: 出力時のキーソート。

**実行例:**

```bash
# 標準入力から辞書を生成
echo "name=test" | dictknife mkdict -o - --output-format yaml
# name: test

# コマンドライン引数からネストした辞書を生成
dictknife mkdict user/name=Alice user/age=30 -o user.json
# user.json の内容: {"user": {"name": "Alice", "age": 30}}
```
```
