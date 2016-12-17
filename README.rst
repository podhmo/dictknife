dictknife
========================================

.. image:: https://travis-ci.org/podhmo/dictknife.svg?branch=master
  :target: https://travis-ci.org/podhmo/dictknife

features

- deepmerge
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

using `LooseDictWalker` example.

.. code-block:: python

  import json
  import pprint
  from dictknife import LooseDictWalker

  refs = []


  def on_has_ref(path, d):
      refs.append((path[:], d["$ref"]))

  walker = LooseDictWalker(on_container=on_has_ref)

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

  walker.walk(["$ref"], d)
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
