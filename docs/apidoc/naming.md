```markdown
# `dictknife.naming`

このモジュールは、文字列の命名規則を変換するための関数群を提供します。例えば、スネークケース、ケバブケース、キャメルケース、パスカルケース間の変換や、文字列の正規化などを行います。

## `normalize(name, ignore_rx=re.compile("[^0-9a-zA-Z_]+"))`

与えられた `name` 文字列を正規化します。デフォルトでは、ハイフン `-` をアンダースコア `_` に置換した後、英数字とアンダースコア以外の文字をすべて除去します。

*   `name`: 正規化する文字列。
*   `ignore_rx`: 除去する文字パターンを指定する正規表現オブジェクト。デフォルトは `[^0-9a-zA-Z_]+`。

**戻り値:** 正規化された文字列。

**実行例:**

```python
from dictknife.naming import normalize

name1 = normalize("My-Variable Name 123")
# name1 is "My_VariableName_123"

name2 = normalize("foo-bar*baz")
# name2 is "foo_barbaz"

# カスタム正規表現でアンダースコアも除去する例
import re
name3 = normalize("My_Variable_Name", ignore_rx=re.compile("[^0-9a-zA-Z]+"))
# name3 is "MyVariableName"
```

## `snakecase(name, *, rx0=..., rx1=..., separator="_", other="-")`

文字列 `name` をスネークケース (例: `snake_case_example`) に変換します。
内部的に正規表現 `rx0` と `rx1` を使用して大文字と小文字の境界を検出し、`separator` (デフォルトは `_`) で区切ります。また、`other` (デフォルトは `-`) で指定された文字も `separator` に置換します。

*   `name`: 変換する文字列。
*   `separator`: 単語区切りに使用する文字。デフォルトは `_`。
*   `other`: `separator` に置換される追加の文字。デフォルトは `-`。

**戻り値:** スネークケースに変換された文字列。

**実行例:**

```python
from dictknife.naming import snakecase

s1 = snakecase("CamelCaseName")
# s1 is "camel_case_name"

s2 = snakecase("PascalCaseName")
# s2 is "pascal_case_name"

s3 = snakecase("already_snake_case")
# s3 is "already_snake_case"

s4 = snakecase("kebab-case-name")
# s4 is "kebab_case_name"

s5 = snakecase("HTTPResponseCode")
# s5 is "http_response_code"

s6 = snakecase("ABcDEF") # 連続する大文字の扱い
# s6 is "a_bc_def"
```

## `kebabcase(name, *, rx0=..., rx1=..., separator="-", other="_")`

文字列 `name` をケバブケース (例: `kebab-case-example`) に変換します。
`snakecase` と同様のロジックですが、デフォルトの `separator` が `-`、`other` が `_` になります。

*   `name`: 変換する文字列。
*   `separator`: 単語区切りに使用する文字。デフォルトは `-`。
*   `other`: `separator` に置換される追加の文字。デフォルトは `_`。

**戻り値:** ケバブケースに変換された文字列。

**実行例:**

```python
from dictknife.naming import kebabcase

k1 = kebabcase("CamelCaseName")
# k1 is "camel-case-name"

k2 = kebabcase("PascalCaseName")
# k2 is "pascal-case-name"

k3 = kebabcase("already-kebab-case")
# k3 is "already-kebab-case"

k4 = kebabcase("snake_case_name")
# k4 is "snake-case-name"

k5 = kebabcase("HTTPResponseCode")
# k5 is "http-response-code"
```

## `camelcase(name, *, soft=True)`

文字列 `name` をキャメルケース (例: `camelCaseExample`) に変換します。

*   `name`: 変換する文字列。
*   `soft=True` (デフォルト): もし `name` の最初の文字が大文字の場合、パスカルケース (`PascalCaseExample`) として扱います。`False` の場合は、最初の文字が小文字になるように強制します。

**戻り値:** キャメルケースまたはパスカルケースに変換された文字列。

**実行例:**

```python
from dictknife.naming import camelcase

c1 = camelcase("snake_case_name")
# c1 is "snakeCaseName"

c2 = camelcase("kebab-case-name")
# c2 is "kebabCaseName"

c3 = camelcase("PascalCaseName") # soft=True なので PascalCase のまま
# c3 is "PascalCaseName"

c4 = camelcase("PascalCaseName", soft=False) # soft=False なので先頭小文字
# c4 is "pascalCaseName"

c5 = camelcase("alreadyCamelCase")
# c5 is "alreadyCamelCase"

c6 = camelcase("Title Case Name")
# c6 is "TitleCaseName" (pascalcase経由)
```

## `pascalcase(name, rx=re.compile(r"[\-_ ]"))`

文字列 `name` をパスカルケース (例: `PascalCaseExample`) に変換します。デフォルトでは、アンダースコア `_`、ハイフン `-`、スペース ` ` を区切り文字として単語に分割し、各単語の先頭を大文字にして結合します。

*   `name`: 変換する文字列。
*   `rx`: 単語の区切り文字を定義する正規表現。デフォルトは `[\-_ ]`。

**戻り値:** パスカルケースに変換された文字列。

**実行例:**

```python
from dictknife.naming import pascalcase

p1 = pascalcase("snake_case_name")
# p1 is "SnakeCaseName"

p2 = pascalcase("kebab-case-name")
# p2 is "KebabCaseName"

p3 = pascalcase("camelCaseName") # 先頭も大文字になる
# p3 is "CamelCaseName"

p4 = pascalcase("a_b_c")
# p4 is "ABC"

p5 = pascalcase("alreadyPascalCase")
# p5 is "AlreadyPascalCase" (最初の単語として扱われる)

p6 = pascalcase("title case words")
# p6 is "TitleCaseWords"
```

## `titleize(name)`

文字列 `name` の最初の文字を大文字にし、残りの文字はそのままにします (いわゆるタイトルケースとは異なり、単語の先頭を全て大文字化するわけではありません)。

*   `name`: 変換する文字列。

**戻り値:** 最初の文字が大文字化された文字列。`name` が空の場合は空文字列を返します。

**実行例:**

```python
from dictknife.naming import titleize

t1 = titleize("hello")
# t1 is "Hello"

t2 = titleize("world")
# t2 is "World"

t3 = titleize("AlreadyTitled")
# t3 is "AlreadyTitled"

t4 = titleize("")
# t4 is ""

t5 = titleize("1st")
# t5 is "1st" (最初の文字が非アルファベットの場合、そのまま)
```

## `untitleize(name)`

文字列 `name` の最初の文字を小文字にし、残りの文字はそのままにします。

*   `name`: 変換する文字列。

**戻り値:** 最初の文字が小文字化された文字列。`name` が空の場合は空文字列を返します。

**実行例:**

```python
from dictknife.naming import untitleize

u1 = untitleize("Hello")
# u1 is "hello"

u2 = untitleize("WORLD")
# u2 is "wORLD"

u3 = untitleize("alreadyUntitled")
# u3 is "alreadyUntitled"

u4 = untitleize("")
# u4 is ""

u5 = untitleize("1St")
# u5 is "1St" (最初の文字が非アルファベットの場合、そのまま)
```
```
