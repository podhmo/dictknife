import json
import yaml
from io import StringIO


def loads(s):
    return yaml.load(StringIO(s))

defs = """
definitions:
  my:
    type: object
    properties:
      foo:
        type: string
      bar:
        $ref: "#/definitions/my"
  myExtended:
    $merge:
      source:
        $ref: "#/definitions/my"
      with:
        properties:
          baz:
            type: number
          foo:
            null
""".strip()

from dictknife.jsonknife.resolver import OneDocResolver
from dictknife.jsonknife.expander import Expander
from dictknife import pp
doc = loads(defs)
resolver = OneDocResolver(doc)
expander = Expander(resolver)
pp(expander.expand())
