# as command (dictknife)

- concat
- diff
- transform

## concat

1. Concat dict like data(JSON, YAML).

```bash
$ dictknife cat --format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
{
  "name": "foo",
  "age": 20
}
```

2. convert file type (e.g. JSON to YAML)

```bash
# json to yaml
$ dictknife cat --output-format yaml --input-format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
name: foo
age: 20

# json to toml
$ dictknife cat --output-format toml --input-format json <(echo '{"name": "foo"}') <(echo '{"age": 20}')
name = "foo"
age = 20
```

## diff

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

### normalize option

If input data is yaml format, the types of keys are maybe not one type.

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

### more normalize option

If your data is array, then, another tool something like jq, sorting is not supported.

For example, in the situation like a below.

```
$ cat <<-EOS > people0.json
[
  {
    "name": "foo",
    "age": 10
  },
  {
    "name": "bar",
    "age": 20
  }
]
EOS
$ cat <<-EOS > people1.json
[
  {
    "name": "bar",
    "age": 20
  },
  {
    "name": "foo",
    "age": 10
  }
]
EOS

# jq's -S is not working
$ diff -u <(jq -S . people0.json) <(jq -S . people1.json)
--- /dev/fd/63	2017-06-10 15:41:12.000000000 +0900
+++ /dev/fd/62	2017-06-10 15:41:12.000000000 +0900
@@ -1,10 +1,10 @@
 [
   {
-    "age": 10,
-    "name": "foo"
-  },
-  {
     "age": 20,
     "name": "bar"
+  },
+  {
+    "age": 10,
+    "name": "foo"
   }
 ]

# of cource, using sort_by is working (but it is needed that structural knowledge about data).
$ diff -u <(jq -S "sort_by(.name)" people0.json) <(jq -S "sort_by(.name)" people1.json)
```

we can check diff with `--normalize` option only.

```bash
dictknife diff --normalize people0.json people1.json
```


## transform

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
