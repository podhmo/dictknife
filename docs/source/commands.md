# commands

## dictknife

- concat
- diff
- transform

### concat

1. Concat dict like data(JSON, YAML).

```bash
$ dictknife concat --format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
{
  "name": "foo",
  "age": 20
}
```

2. convert file type (e.g. JSON to YAML)

```bash
# json to yaml
$ dictknife concat --output-format yaml --input-format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
name: foo
age: 20

# json to toml
$ dictknife concat --output-format toml --input-format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
name = "foo"
age = 20
```

### diff

json diff

```bash
$ cat <<-EOS > person0.yaml
person:
  name: foo
  age: 20
EOS
$ cat <<-EOS > person1.yaml
person:
  age: 20
  name: foo
EOS
$ dictknife diff person{0,1}.yaml
```

```bash
$ cat <<-EOS > person2.yaml
person:
  age: 20
  name: bar
  nickname: b
EOS
$ dictknife diff person{0,2}.yaml
--- person0.yaml
+++ person2.yaml
@@ -1,6 +1,7 @@
 {
   "person": {
     "age": 20,
-    "name": "foo"
+    "name": "bar",
+    "nickname": "b"
   }
 }
```

#### normalize option

If input data is yaml format, the type of keys are maybe not one type.

```bash
$ cat <<-EOS > status.yaml
200:
  ok
default:
  hmm
EOS
$ dictknife diff status.yaml status.yaml
TypeError: unorderable types: str() < int()

$ dictknife diff --normalize status.yaml status.yaml
```

### transform

```bash
$ cat status.yaml
200:
  ok
default:
  hmm

$ cat status.yaml | dictknife transform --code='lambda d: [d,d,d]'
- 200: ok
  default: hmm
- 200: ok
  default: hmm
- 200: ok
  default: hmm
```

## jsonknife
