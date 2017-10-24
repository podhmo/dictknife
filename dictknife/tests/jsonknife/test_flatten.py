import unittest


class Tests(unittest.TestCase):
    def _makeOne(self, *args, **kwargs):
        from dictknife.swaggerknife.flatten import Flattener
        return Flattener(*args, **kwargs)

    def test_it(self):
        import json
        s = """
{
  "definitions": {
    "a": {
      "type": "object",
      "properties": {
        "b": {
          "type": "object",
          "properties": {
            "c": {
              "type": "object",
              "properties": {
                "name": {
                  "type": "string"
                }
              }
            },
            "vs": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "name": {
                    "type": "string"
                  },
                  "value": {
                    "type": "integer"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
        d = json.loads(s)
        target = self._makeOne()
        got = target.flatten(d["definitions"])

        expected = json.loads(
            """
{
  "definitions": {
    "a": {
      "properties": {
        "b": {
          "$ref": "#/definitions/aB"
        }
      },
      "type": "object"
    },
    "aB": {
      "properties": {
        "c": {
          "$ref": "#/definitions/aBC"
        },
        "vs": {
          "$ref": "#/definitions/aBVs"
        }
      },
      "type": "object"
    },
    "aBC": {
      "properties": {
        "name": {
          "type": "string"
        }
      },
      "type": "object"
    },
    "aBVs": {
      "items": {
        "$ref": "#/definitions/aBVsItem"
      },
      "type": "array"
    },
    "aBVsItem": {
      "properties": {
        "name": {
          "type": "string"
        },
        "value": {
          "type": "integer"
        }
      },
      "type": "object"
    }
  }
}
"""
        )
        self.assertEqual(got, expected)
