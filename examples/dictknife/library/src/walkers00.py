from dictknife import loading
from dictknife import DictWalker

# from: https://github.com/BigstickCarpet/json-schema-ref-parser
d = loading.loads(
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
""",
    format="json"
)

walker = DictWalker(["$ref"])
refs = [("/".join(path[:]), sd["$ref"]) for path, sd in walker.walk(d)]

for path, ref in refs:
    print(path, ref)
