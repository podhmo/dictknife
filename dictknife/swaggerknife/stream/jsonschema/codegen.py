import typing as t
from prestring.python import Module
from prestring.naming import pascalcase
from dictknife.swaggerknife.stream import Event
from dictknife.swaggerknife.stream.jsonschema import ToplevelVisitor
from dictknife.swaggerknife.stream.jsonschema import names

# todo: toplevel properties


def gen():
    m = Module()

    with m.class_("ToplevelVisitor", "Visitor"):
        # m.docstring("openAPI v3 node")
        m.stmt("@reify")
        with m.def_("schema", "self"):
            m.stmt("return SchemaVisitor()")

        with m.def_("__call__", "self", "ctx: Context", "d: dict"):
            m.stmt("teardown = ctx.push_name(ctx.resolver.name)")
            m.stmt("self.schema.visit(ctx, d)")
            m.stmt("teardown()")
    print(m)


class Generator:
    def __init__(self, m=None):
        self.m = m or Module(import_unique=True)
        self.visitors = []

    def _iterate_links(self, ev: Event) -> t.Iterable[t.Tuple[str, str]]:
        if names.flavors.has_links not in ev.flavors:
            return []
        return ev.get_annotated(names.annotations.links)

    def _register_visitor(self, ev: Event, clsname: str) -> None:
        self.visitors.append((ev.fullref, clsname))

    def gen_visitor(self, ev: Event, *, m=None, clsname: str = None) -> None:
        m = self.m
        clsname = pascalcase(clsname or ev.get_annotated(names.flavors.has_name))
        self._register_visitor(ev, clsname)

        m.from_("dictknife.swaggerknife.stream", "Visitor")

        with m.class_(clsname, "Visitor"):
            m.stmt(f"schema_type = {ev.name!r}")
            m.stmt(f"flavors = {ev.flavors!r}")
            m.stmt("")

            m.stmt("@reify  # node")
            with m.def_("node", "self"):
                m.stmt(
                    f"""cls = self.registry.resolve_node_from_string(".nodes:{clsname}")"""
                )
                m.return_("cls and cls()")

            with m.def_("__call__", "self", "ctx: Context", "d: dict"):
                with m.if_("self.node is not None"):
                    m.stmt("self.node.attach(ctx, d, self)")

                for name, ref in self._iterate_links(ev):
                    with m.if_(f"{name!r} in d"):
                        m.stmt(
                            f"ctx.run({name!r}, self.{name}, d[{name!r}])", name=name
                        )

            # todo: use helper function
            for name, ref in self._iterate_links(ev):
                m.stmt("@reify  # visitor")
                with m.def_(name, "self"):
                    m.stmt(f"""cls = self.registry.resolve_visitor_from_ref({ref!r})""")
                    m.return_("return cls and cls()")

    def gen_registry(self):
        m = self.m
        with m.def_("get_registry(registry=None)"):
            m.docstring("get default registry")
            m.from_("dictknife.swaggerknife.stream.registry", "DictRegistry")

            m.stmt("registry = registry or DictRegistry()")
            m.stmt("mapping = registry.ref_visitor_mapping")
            for ref, clsname in self.visitors:
                m.stmt(f"mapping[{ref!r}] = {clsname}")
            m.return_("registry")


def main():
    from dictknife.swaggerknife.stream import main

    g = Generator()
    toplevels: t.List[Event] = []

    stream: t.Iterable[Event] = main(create_visitor=ToplevelVisitor)
    for ev in stream:
        if names.flavors.toplevel_properties in ev.flavors:
            toplevels.append(ev)
            continue

        if names.flavors.has_name in ev.flavors:
            g.gen_visitor(ev)
        elif names.flavors.toplevel_properties in ev.flavors:
            print("hmm", ev)

    for ev in toplevels:
        if "#/" not in ev.fullref:
            g.gen_visitor(ev, clsname="toplevel")

    g.gen_registry()

    print(g.m)


if __name__ == "__main__":
    main()
