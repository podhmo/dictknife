```markdown
# `dictknife.cliutils.extraarguments`

このモジュールは、Pythonの `argparse` を拡張し、特定のオプションの値に応じて動的に変化する「追加の引数 (extra arguments)」をパースする仕組みを提供します。

例えば、`mycommand --format json --json-sort-keys` のように、`--format` オプションの値が `json` である場合にのみ `--json-sort-keys` という追加オプションを有効にしたい、といったシナリオで使用されます。`dictknife` のコマンドラインツールでは、出力フォーマット (`--format yaml` など) に応じて、そのフォーマット固有のオプション (例: YAMLのインデント設定) を受け付けるために利用されています。

## `ExtraArgumentsParsers` クラス

メインとなる `argparse.ArgumentParser` にバインドし、追加引数の定義とパースを管理します。

### `__init__(self, parser, dest, *, prefix="extra", parser_factory=argparse.ArgumentParser)`

*   `parser`: メインとなる `argparse.ArgumentParser` インスタンス。
*   `dest`: 追加引数が関連付けられるメインパーサーのオプション名 (例: `--format` オプションの場合、`dest` は通常 `"format"`)。
*   `prefix="extra"` (デフォルト): 追加引数をコマンドラインで指定する際のプレフィックス。例えば `prefix="extra"` の場合、追加引数 `sort_keys` は `--extra-sort-keys` として指定します。
*   `parser_factory=argparse.ArgumentParser`: 追加引数用の内部パーサーを生成するためのファクトリ。

初期化時に、メインパーサーのヘルプメッセージ生成機能 (`format_help`) が拡張され、定義された追加引数のヘルプも表示されるようになります。

### `add_parser(self, name)`

`dest` オプションが取りうる特定の値 `name` (例: `"json"`, `"yaml"`) に対応する追加引数用の新しい `ArgumentParser` インスタンスを作成し、返します。
返されたパーサーに対して、通常の `argparse` と同様に `add_argument()` を使って、その `name` が選択された場合にのみ有効になる引数を定義できます。

**例:**
```python
main_parser = ArgumentParser("mycmd")
main_parser.add_argument("--output-format", default="json", choices=["json", "yaml"])

extra_parsers = ExtraArgumentsParsers(main_parser, dest="output_format", prefix="format")

# "--output-format json" の時だけ有効なオプション
json_extra_parser = extra_parsers.add_parser("json")
json_extra_parser.add_argument("--sort-keys", action="store_true", help="JSON出力でキーをソートする")
json_extra_parser.add_argument("--indent", type=int, help="JSON出力のインデント数")

# "--output-format yaml" の時だけ有効なオプション
yaml_extra_parser = extra_parsers.add_parser("yaml")
yaml_extra_parser.add_argument("--default-flow-style", action="store_false", help="YAML出力のデフォルトフロースタイル")
```

### `parse_args(self, name, args)`

指定された `name` (例: `"json"`) に対応する追加引数パーサーを使って、`args` (追加引数のリスト、例: `['--format-sort-keys', '--format-indent', '2']`) をパースします。

*   `name`: `dest` オプションが取った値。
*   `args`: パース対象の追加引数文字列のリスト。プレフィックス (`--<prefix>-`) が付いている必要があります。
*   パースされた結果 (名前空間オブジェクト) を返します。
*   定義されていない追加引数が `args` に含まれていた場合、警告を標準エラーに出力して無視します。

### ヘルプメッセージの拡張

`ExtraArgumentsParsers` をバインドすると、メインパーサーのヘルプメッセージ (`python mycmd.py -h`) に、以下のように追加引数の説明が自動的に付加されます。

```
usage: mycmd [-h] [--output-format {json,yaml}] ...

options:
  -h, --help            show this help message and exit
  --output-format {json,yaml}

format arguments: (with --format-<option>)
  for output_format=json:
    --sort-keys       JSON出力でキーをソートする
    --indent INDENT   JSON出力のインデント数
  for output_format=yaml:
    --default-flow-style
                        YAML出力のデフォルトフロースタイル
```

これにより、ユーザーは特定のオプション選択時に利用可能な追加オプションを容易に知ることができます。
```
