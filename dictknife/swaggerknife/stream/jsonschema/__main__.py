from dictknife.swaggerknife.stream import main
from dictknife.swaggerknife.stream.jsonschema import ToplevelVisitor

# python -m dictknife.swaggerknife.stream.jsonschema

if __name__ == "__main__":
    main(create_visitor=ToplevelVisitor)
