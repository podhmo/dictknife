import pathlib
from dictknife.jsonknife import get_resolver
from dictknife import loading

filename = pathlib.Path(__file__) / "../data/resolver/xxx.json"
resolver = get_resolver(filename)
d = resolver.access_by_json_pointer("/definitions/Foo")
loading.dumpfile(d, format="json")
