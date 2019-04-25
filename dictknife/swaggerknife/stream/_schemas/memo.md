- additionalProperties
- patternProperties
- oneOf
- allOf
- anyOf

## walker strategy

- start from `#/properties`
- see `#/definitions`
- see "$ref"
- hmm, oneOf ["x","Reference]

## encode

oneOf [x,y,z]

```python
matched = 0
if is_x():
    do_x()
    matched += 1

if is_y():
    do_y()
    matched += 1

if is_z():
    do_z()
    matched += 1

if matched == 0 or matched > 1:
    raise Exception()
```

allOf [x,y,z]

```python
do_x()
do_y()
do_z()
```

anyOf [x,y,z]

```python
matched = 0

if is_x():
    do_x()
    matched += 1
if is_y():
    do_y()
    matched += 1
if is_z():
    do_z()
    matched += 1

if matched == 0:
    raise Exception()
```

## simplify

```python
matched = 0

for p, do in candidates:
    if p():
        do()
        matched += 1
assertion(match)
```
