dictknife
========================================

.. image:: https://travis-ci.org/podhmo/dictknife.svg?branch=master
  :target: https://travis-ci.org/podhmo/dictknife

features

- deepmerge
- deepequal
- walker


deepmerge
----------------------------------------

.. code-block:: python

  from dictknife import deepmerge
  d0 = {
      "a": {
          "x": 1
      },
      "b": {
          "y": 10
      },
  }
  d1 = {
      "a": {
          "x": 1
      },
      "b": {
          "z": 10
      },
      "c": 100
  }
  actual = self._callFUT(d0, d1)
  expected = {
      "a": {
          "x": 1
      },
      "b": {
          "y": 10,
          "z": 10
      },
      "c": 100
  }
  assert actual == expected


walker
----------------------------------------

using `LooseDictWalkingIterator` example.

.. code-block:: python

  import json
  import pprint
  from dictknife import LooseDictWalkingIterator

  # from: https://github.com/BigstickCarpet/json-schema-ref-parser
  d = json.loads("""
  {
    "definitions": {
      "person": {
        "$ref": "schemas/people/Bruce-Wayne.json"
      },
      "place": {
        "$ref": "schemas/places.yaml#/definitions/Gotham-City"
      },
      "thing": {
        "$ref": "http://wayne-enterprises.com/things/batmobile"
      },
      "color": {
        "$ref": "#/definitions/thing/properties/colors/black-as-the-night"
      }
    }
  }
  """)

  refs = []

  iterator = LooseDictWalkingIterator(["$ref"])
  for path, sd in iterator.iterate(d):
      refs.append((path[:], sd["$ref"]))

  pprint.pprint(refs)

output

.. code-block:: python

  [(['definitions', 'color', '$ref'],
    '#/definitions/thing/properties/colors/black-as-the-night'),
   (['definitions', 'place', '$ref'],
    'schemas/places.yaml#/definitions/Gotham-City'),
   (['definitions', 'thing', '$ref'],
    'http://wayne-enterprises.com/things/batmobile'),
   (['definitions', 'person', '$ref'], 'schemas/people/Bruce-Wayne.json')]


todo: description about chains and operator and context,...

command
----------------------------------------

install dictknife via `pip install dictknife[command]`.

- concat
- transform
- diff

TODO: gentle introduction

concat
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  $ dicknife concat a.yaml b.yaml c.json

transform
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  $ transform --function misc/transform.py:lift --src src/01transform/properties.yaml --config '{"name": "person"}'
  # or
  $ dictknife transform --code 'lambda d,**kwargs: {"definitions": {"person": d}}' --src src/01transform/properties.yaml


diff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  $ dictknife diff a.yaml b.yaml
  $ dictknife diff --sort-keys a.yaml b.yaml
