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

[(['definitions', 'color', '$ref'],
  '#/definitions/thing/properties/colors/black-as-the-night'),
 (['definitions', 'place', '$ref'],
  'schemas/places.yaml#/definitions/Gotham-City'),
 (['definitions', 'thing', '$ref'],
  'http://wayne-enterprises.com/things/batmobile'),
 (['definitions', 'person', '$ref'], 'schemas/people/Bruce-Wayne.json')]
