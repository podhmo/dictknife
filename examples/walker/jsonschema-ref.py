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

[(['definitions', 'color', '$ref'],
  '#/definitions/thing/properties/colors/black-as-the-night'),
 (['definitions', 'place', '$ref'],
  'schemas/places.yaml#/definitions/Gotham-City'),
 (['definitions', 'thing', '$ref'],
  'http://wayne-enterprises.com/things/batmobile'),
 (['definitions', 'person', '$ref'], 'schemas/people/Bruce-Wayne.json')]
