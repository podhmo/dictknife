import json
from dictknife import LooseDictWalkingIterator

# from: https://github.com/BigstickCarpet/json-schema-ref-parser
d = json.loads(
    """
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
"""
)

iterator = LooseDictWalkingIterator(["$ref"])
refs = [("/".join(path[:]), sd["$ref"]) for path, sd in iterator.iterate(d)]

for path, ref in refs:
    print(path, ref)
