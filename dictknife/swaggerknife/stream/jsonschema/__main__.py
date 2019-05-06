from dictknife.swaggerknife.stream import main
from dictknife.swaggerknife.stream.jsonschema import ToplevelVisitor

# python -m dictknife.swaggerknife.stream.jsonschema

if __name__ == "__main__":
    for ev in main(create_visitor=ToplevelVisitor):
        if "primitive" in ev.roles:
            continue
        print(ev)
