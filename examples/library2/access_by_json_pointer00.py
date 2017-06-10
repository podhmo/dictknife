from dictknife import loading
from dictknife.pp import indent
loading.setup()

yaml = """
definitions:
  person:
    type: object
    properties:
      name:
        type: string
      age:
        type: integer
"""
d = loading.loads(yaml, format="yaml")

with indent(2, "load data\n"):
    print(loading.dumps(d, format="yaml"))

with indent(2, "access by json pointer\n"):
    from dictknife.jsonknife import access_by_json_pointer

    q = "/definitions/person/properties"
    v = access_by_json_pointer(d, q)
    print("access : {}".format(q))
    print(loading.dumps(v, format="yaml"))

    # this is also ok(but this is json reference).
    q = "#/definitions/person/properties"
    v = access_by_json_pointer(d, q)
    print("access : {}".format(q))
    print(loading.dumps(v, format="yaml"))

with indent(2, "assign by json pointer\n"):
    from dictknife.jsonknife import assign_by_json_pointer

    q = "/definitions/person/properties/nickname"
    v = {"type": "string"}
    assign_by_json_pointer(d, q, v)
    print("assign : {} = {}".format(q, v))
    print(loading.dumps(d, format="yaml"))
