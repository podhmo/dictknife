import unittest
import textwrap
import yaml
from io import StringIO


def loads(s):
    return yaml.load(StringIO(s))


class Tests(unittest.TestCase):
    def _callFUT(self, doc):
        from dictknife.jsonknife.resolver import OneDocResolver
        from dictknife.jsonknife.expander import Expander
        expander = Expander(OneDocResolver(doc))
        return expander.expand()

    def assert_defs(self, actual, expected):
        from dictknife import diff
        self.assertEqual("\n".join(diff(expected, actual)), "")

    def test_self_recursion(self):
        defs_text = textwrap.dedent("""
        definitions:
          foo:
            type: string
          my:
            type: object
            properties:
              foo:
                $ref: "#/definitions/foo"
              bar:
                $ref: "#/definitions/my"
        """)
        defs = loads(defs_text)
        actual = self._callFUT(defs)
        expected = {
            'definitions': {
                'foo': {
                    'type': 'string',
                },
                'my': {
                    'type': 'object',
                    'properties': {
                        'foo': {
                            'type': 'string'
                        },
                        'bar': {
                            '$ref': '#/definitions/my'
                        }
                    }
                }
            }
        }
        self.assert_defs(actual, expected)

    def test_mutual_recursion(self):
        defs_text = textwrap.dedent("""
        definitions:
          text_assets:
            properties:
              asset:
                $ref: "#/definitions/asset_image"
          asset_image:
            properties:
              caption:
                $ref: "#/definitions/text_assets"
        """)
        defs = loads(defs_text)
        actual = self._callFUT(defs)
        expected = {
            'definitions': {
                'text_assets': {
                    'properties': {
                        'asset': {
                            '$ref': '#/definitions/asset_image'
                        }
                    }
                },
                'asset_image': {
                    'properties': {
                        'caption': {
                            'properties': {
                                'asset': {
                                    '$ref': '#/definitions/asset_image'
                                }
                            }
                        }
                    }
                }
            }
        }
        self.assert_defs(actual, expected)
