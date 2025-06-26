```markdown
# `dictknife.loading`

`dictknife.loading` パッケージは、様々なデータフォーマットの読み込み (load) と書き出し (dump) を行うための統一的なフレームワークを提供します。これにより、`dictknife` の各ツールはファイル形式を意識することなく、構造化データを透過的に扱うことができます。

## 主要なコンセプト

*   **`Dispatcher`**: 中心的な役割を担い、ファイル拡張子や指定されたフォーマット名に基づいて、適切なロード/ダンプ関数を割り当てます。グローバルインスタンス `dictknife.loading.dispatcher` が存在します。
*   **`Loader`**: `dispatcher` の一部として機能し、データの読み込み処理を担当します。
*   **`Dumper`**: `dispatcher` の一部として機能し、データの書き出し処理を担当します。
*   **フォーマット固有モジュール**: `json.py`, `yaml.py`, `csv.py` など、各フォーマットに対応する実際の読み書きロジックを実装したモジュール群。これらは通常、対応するPythonライブラリ (例: `json`, `ruamel.yaml`, `tomlkit`, `csv`) をラップします。

## 提供される関数 (ショートカット)

`dictknife.loading` モジュールから直接インポートして使用できる主要な関数です。これらは内部でグローバルな `dispatcher` を利用します。

*   **`load(fp, format=None, errors=None)`**:
    ファイルポインタ `fp` からデータをロードします。
    *   `format`: フォーマットを明示的に指定 (例: `"json"`, `"yaml"`)。省略時は `fp.name` (ファイル名) の拡張子から推測されます。
    *   `errors`: (主にCSVなどで) パースエラー時の処理方法。
*   **`loads(s, format=None, ...)`**:
    文字列 `s` からデータをロードします。内部で `StringIO(s)` を `load()` に渡します。
*   **`loadfile(filename=None, format=None, opener=None, encoding=None, errors=None)`**:
    ファイル名 `filename` からデータをロードします。`filename` が `None` または `sys.stdin` の場合は標準入力から読み込みます。
    *   `opener`: 特殊なファイルオープン処理が必要な場合に指定 (例: Google Spreadsheet)。
    *   `encoding`: ファイルのエンコーディング。
*   **`dump(d, fp, *, format=None, sort_keys=False, extra=None)`**:
    データ `d` をファイルポインタ `fp` に指定されたフォーマットで書き出します。
    *   `format`: 出力フォーマット。省略時は `fp.name` から推測。
    *   `sort_keys=False`: (主にJSON, YAMLで) キーをソートするかどうか。
    *   `extra=None`: フォーマット固有の追加オプションを辞書で渡します。
*   **`dumps(d, *, format=None, sort_keys=False, extra=None, **kwargs)`**:
    データ `d` を指定されたフォーマットの文字列として返します。
*   **`dumpfile(d, filename=None, *, format=None, sort_keys=False, extra=None)`**:
    データ `d` をファイル名 `filename` に書き出します。`filename` が `None` または `sys.stdout` の場合は標準出力に書き出します。ファイル書き出し時に親ディレクトリが存在しなければ作成します。
*   **`guess_format(filename, *, default=unknown)`**:
    ファイル名からフォーマットを推測します。
*   **`get_opener(*, format=None, filename=None, default=open)`**:
    フォーマットやファイル名に適したファイルオープナー関数を取得します。
*   **`get_formats()`**:
    現在登録されている利用可能なフォーマット名のリストを返します。
*   **`setup(input=None, output=None)`**:
    ファイル拡張子からフォーマットが推測できない場合のデフォルトの入力/出力処理関数 (通常は `yaml.load`/`yaml.dump`) を上書きします。

## 対応フォーマットと関連モジュール

`dictknife.loading.dispatcher` には、以下のフォーマットがデフォルトで登録されています。

| フォーマット名 | 拡張子 (例)           | 依存ライブラリ (主なもの) | ロードモジュール/関数                                  | ダンプモジュール/関数                                   | 備考                                                                             |
|----------------|-----------------------|---------------------------|------------------------------------------------------|-------------------------------------------------------|----------------------------------------------------------------------------------|
| `json`         | `.json`, `.js`        | (標準 `json`)             | `json.load` (標準 `json` + `OrderedDict`)            | `json.dump` (標準 `json`, indent=2, ensure_ascii=False) | キーの順序は保持される傾向。                                                           |
| `yaml`         | `.yaml`, `.yml`       | `ruamel.yaml`             | `yaml.load` (`ruamel.yaml` round-trip)               | `yaml.dump` (`ruamel.yaml` round-trip)                | コメントやスタイルを極力保持。エイリアスは出力しない。                                   |
| `toml`         | `.toml`               | `tomlkit`                 | `toml.load` (`tomlkit`)                              | `toml.dump` (`tomlkit`)                               |                                                                                  |
| `csv`          | `.csv`                | (標準 `csv`)              | `csv.load` (標準 `csv` + 型推測, エラー処理)         | `csv.dump` (標準 `csv`)                               | `--fullscan` オプションで全行からヘッダ生成可。                                        |
| `tsv`          | `.tsv`                | (標準 `csv`)              | `tsv.load` (`csv.load` の `delimiter='\t'` 版)       | `tsv.dump` (`csv.dump` の `delimiter='\t'` 版)        |                                                                                  |
| `md`           | `.md`, `.mdtable`     | -                         | `md.load` (Markdownテーブル)                         | `md.dump` (Markdownテーブル)                          | 数値列の自動判定、`null_value` の指定。                                               |
| `raw`          | (なし)                | -                         | `raw.load` (ファイル全体を文字列としてロード)        | `raw.dump` (文字列をそのままダンプ)                     |                                                                                  |
| `env`          | `.env`, `.environ`    | -                         | `env.load` (テンプレートファイル + 環境変数)           | (なし)                                                | テンプレートの値を環境変数で置換。型変換指定可 (`VAR:int`)。                               |
| `spreadsheet`  | (URL/IDパターン)      | `google-api-python-client`, `google-auth-oauthlib` | `spreadsheet.load` (Google Spreadsheet)            | (未実装)                                              | URLやIDで指定。1行目をヘッダとする辞書のリストを返す (デフォルト)。範囲未指定時はシート情報。 |
| `(unknown)`    | (上記以外)            | `ruamel.yaml` (デフォルト) | `yaml.load` (デフォルト)                             | `yaml.dump` (デフォルト)                              | `setup()` で変更可能。                                                              |

**実行例:**

```python
from dictknife import loading

# JSONファイルのロード
data_json = loading.loadfile("config.json")

# YAML文字列のロード
yaml_string = "name: MyApp\nversion: 1.0"
data_yaml = loading.loads(yaml_string, format="yaml")

# 辞書データをTOMLファイルにダンプ
my_data = {"user": {"name": "Alice", "age": 30}}
loading.dumpfile(my_data, "output.toml", format="toml")

# CSVデータをロード (型推測あり)
# data.csv:
# name,age,active
# Bob,25,true
# Carol,,"false"
csv_data = loading.loadfile("data.csv")
# csv_data は [{'name': 'Bob', 'age': 25, 'active': True}, {'name': 'Carol', 'age': None, 'active': False}] のようになる

# Markdownテーブルとしてダンプ
table_data = [{"id":1, "value":"foo"}, {"id":2, "value":"bar"}]
loading.dumpfile(table_data, "output.md", format="md")

# envフォーマットの例
# template.env.yaml の内容:
#   app_name: APP_NAME
#   debug_mode: DEBUG_MODE:bool
#   port_number: PORT:int
# 環境変数として APP_NAME="MyAPP", DEBUG_MODE="true", PORT="8080" が設定されている場合:
# env_data = loading.loadfile("template.env.yaml")
# env_data は {'app_name': 'MyAPP', 'debug_mode': True, 'port_number': 8080} のようになる

# Google Spreadsheet の例 (別途認証設定が必要)
# sheet_url = "https://docs.google.com/spreadsheets/d/<your_sheet_id>/edit#gid=0"
# sheet_data = loading.loadfile(sheet_url, format="spreadsheet")
# sheet_data は1行目をヘッダとする辞書のリスト (例: [{'colA': 'valA1', 'colB': 'valB1'}, ...])
# または、範囲指定がない場合などでシート情報が返ることもあります。
```

### フォーマット固有オプション (`extra`引数)

`dump` や `dumpfile` の `extra` 引数を通じて、各フォーマットのダンプ関数に固有のオプションを渡すことができます。
例えば、`json.dump` は `indent` や `ensure_ascii` を `extra` で受け取ることができますが、`dictknife.loading.json.dump` のシグネチャで既にデフォルト値が設定されているため、通常は明示的に `extra` を使う必要は少ないかもしれません。コマンドラインツールでは、これらのオプションは `--<format>-<option_name>` (例: `--json-indent`) のような形で `ExtraArgumentsParsers` を介して渡されます。
```
