import typing as t
import json
import logging
from prestring.python import Module
from prestring.naming import pascalcase
from dictknife.swaggerknife.stream import Event
from dictknife.swaggerknife.stream.jsonschema import ToplevelVisitor
from dictknife.swaggerknife.stream.jsonschema import names

logger = logging.getLogger(__name__)


class _LazyName:
    def __init__(self, callable: t.Callable[[], str]) -> None:
        self.callable = callable

    def __str__(self) -> str:
        return self.callable()


# todo: oneOf,anyof,allOf
# todo: additionalProperties (schema)
# todo: anonymous definition(nested definition)
# todo: anonymous definition(oneOf, anyof, allOf)


class Helper:
    def classname(self, ev: Event, *, clsname: str = None) -> str:
        return pascalcase(clsname or ev.get_annotated(names.annotations.name))

    def has_pattern_properties(self, ev: Event) -> bool:
        return (
            names.roles.has_extra_properties in ev.roles
            and "patternProperties" in ev.data
        )

    def has_additional_properties(self, ev: Event) -> bool:
        return (
            names.roles.has_extra_properties in ev.roles
            and "additionalProperties" in ev.data
        )

    def iterate_links(self, ev: Event) -> t.Iterable[t.Tuple[str, str]]:
        if names.roles.has_links not in ev.roles:
            return []
        return ev.get_annotated(names.annotations.links)

    def iterate_xxx_of_links(self, ev: Event) -> t.Iterable[t.Tuple[str, str]]:
        return ev.get_annotated(names.annotations.xxx_of_links)


class NameManager:  # todo: rename
    def __init__(self):
        self.visitors = {}

    def register_visitor_name(self, ev: Event, clsname):
        self.visitors[ev.uid] = clsname

    def create_lazy_visitor_name(self, ref: str) -> _LazyName:
        def to_str(ref: str = ref):
            name = self.visitors[ref]
            # name = self.visitors.get(ref) or "<missing>"
            logger.debug("resolve clasname: %s -> %s", ref, name)
            return name

        return _LazyName(to_str)


class Emitter:  # todo: rename
    def emit_data(self, m, fmt: str, d: dict, *, nofmt=False):
        """emit data as python literal"""
        if nofmt:
            m.stmt("# fmt: off")
        m.stmt(fmt, json.loads(json.dumps(d)))
        if nofmt:
            m.stmt("# fmt: on")


class Logging:
    def __init__(self, m, *, enable: bool):
        self.enable = enable

        if not hasattr(m, "import_area"):  # xxx:
            m.import_area = m.submodule()

        if self.enable:
            m.import_area.from_("logging", "getLogger")
            m.stmt("logger = getLogger(__name__)  # noqa")
            m.sep()

    def log(self, m, fmt, *args, **kwargs):
        if self.enable:
            m.stmt(fmt, *args, **kwargs)


class Generator:
    def __init__(self, m, logging_enable=True):
        self.m = m

        self.logging = Logging(m, enable=logging_enable)
        self.emitter = Emitter()
        self.helper = Helper()
        self.name_manager = NameManager()

    def generate_class(self, ev: Event, *, m=None, clsname: str = None) -> None:
        m = self.m
        clsname = self.helper.classname(ev, clsname=clsname)
        self.name_manager.register_visitor_name(ev, clsname)

        m.import_area.from_("dictknife.swaggerknife.stream", "Visitor")
        with m.class_(clsname, "Visitor"):
            self._gen_headers(ev, m=m)

            if self.helper.has_pattern_properties(ev):
                self._gen_pattern_properties_regexes(ev, m=m)

            self._gen_node_property(ev, clsname=clsname, m=m)
            self._gen_visit_method(ev, m=m)
            self._gen_visit_private_method(ev, clsname=clsname, m=m)

            # reify properties
            self._gen_properties_visitors(ev, m=m)
            if ev.name in (names.types.oneOf, names.types.allOf, names.types.anyOf):
                self._gen_xxx_of_visitors(ev, m=m)

    def _gen_headers(self, ev: Event, *, m) -> None:
        m.stmt(f"schema_type = {ev.name!r}")
        m.stmt(f"roles = {ev.roles!r}")

        m.stmt(f"_uid = {ev.uid!r}")
        if names.roles.has_properties in ev.roles:
            m.stmt(f"_properties = {ev.get_annotated(names.annotations.properties)!r}")
        if names.roles.has_extra_properties in ev.roles:
            data = ev.get_annotated(names.annotations.extra_properties)
            self.emitter.emit_data(m, "_extra_properties = {}", data)
        if names.roles.has_links in ev.roles:
            m.stmt(
                f"_links = {[name for name, ref in self.helper.iterate_links(ev)]!r}"
            )
        m.sep()

    def _gen_pattern_properties_regexes(self, ev: Event, *, m) -> None:
        m.stmt("@reify  # visitor")
        with m.def_("_pattern_properties_regexes", "self"):
            m.import_("re")
            m.stmt("r = []")
            for k, ref in ev.get_annotated(names.annotations.pattern_properties_links):
                if ref is None:
                    m.stmt("""r.append((re.compile({k!r}), None))""", k=k)
                    continue

                lazy_name = self.name_manager.create_lazy_visitor_name(ref)
                m.stmt("""r.append((re.compile({k!r}), {cls}()))""", k=k, cls=lazy_name)
            m.return_("r")

    def _gen_node_property(self, ev: Event, *, clsname, m) -> None:
        m.stmt("@reify  # todo: use Importer")
        with m.def_("node", "self"):
            with m.try_():
                self.logging.log(
                    m, f"""logger.debug("resolve node: %s", {clsname!r})"""
                )
                m.submodule().from_(".nodes", clsname)
                m.return_("{}()", clsname)
            with m.except_("ImportError"):
                self.logging.log(
                    m, f"""logger.info("resolve node: %s is not found", {clsname!r})"""
                )
                m.return_("None")

    def _gen_visit_method(self, ev: Event, *, m) -> None:
        with m.def_("__call__", "self", "ctx: Context", "d: dict"):
            if ev.name == names.types.array:
                m.return_("[self._visit(ctx, x) for x in d]")
            elif names.roles.primitive_type in ev.roles:
                # drop schema definitions?
                m.return_("self._visit(ctx, d)  # todo: simplify")
            elif names.roles.combine_type in ev.roles:
                expanded = ev.get_annotated(names.annotations.expanded)
                links = list(self.helper.iterate_xxx_of_links(ev))
                bodies = {k: v for k, v in expanded.items() if k != "definitions"}
                m.stmt("# for {} (xxx: _case is module global)", ev.name)

                if ev.name == names.types.oneOf:
                    for i, prop in enumerate(bodies["oneOf"]):
                        with m.if_(f"_case.when(d, {prop['$ref']!r})"):
                            ref = links[i]
                            if ref is None:
                                m.stmt("return  # not supported yet")
                                continue  # xxx
                            else:
                                m.stmt(
                                    f"return ctx.run(None, self.{ev.name}{i!r}.visit, d)"
                                )
                    m.stmt("raise ValueError('unexpected value')  # todo gentle message")
                elif ev.name == names.types.anyOf:
                    m.stmt("matched = False")
                    for i, prop in enumerate(bodies["anyOf"]):
                        with m.if_(f"_case.when(d, {prop['$ref']!r})"):
                            ref = links[i]
                            if ref is None:
                                m.stmt("pass  # not supported yet")
                                continue  # xxx
                            else:
                                m.stmt("matched = True")
                                m.stmt(
                                    f"ctx.run(None, self.{ev.name}{i!r}.visit, d)"
                                )
                    with m.if_("not matched"):
                        m.stmt("raise ValueError('unexpected value')  # todo gentle message")
                elif ev.name == names.types.allOf:
                    for i, prop in enumerate(bodies["anyOf"]):
                        with m.if_(f"not _case.when(d, {prop['$ref']!r})"):
                            m.stmt("raise ValueError('unexpected value')  # todo gentle message")
                        ref = links[i]
                        if ref is None:
                            m.stmt("pass  # not supported yet")
                            continue  # xxx
                        else:
                            m.stmt(
                                f"ctx.run(None, self.{ev.name}{i!r}.visit, d)"
                            )
            else:
                m.return_("self._visit(ctx, d)  # todo: remove this code")

    def _gen_visit_private_method(self, ev: Event, *, clsname: str, m) -> None:
        with m.def_("_visit", "self", "ctx: Context", "d: dict"):
            self.logging.log(m, f"""logger.debug("visit: %s", {clsname!r})""")

            with m.if_("self.node is not None"):
                m.stmt("self.node.attach(ctx, d, self)")

            for name, ref in self.helper.iterate_links(ev):
                with m.if_(f"{name!r} in d"):
                    m.stmt(
                        f"ctx.run({name!r}, self.{name}.visit, d[{name!r}])", name=name
                    )

            if self.helper.has_pattern_properties(ev):
                m.sep()
                m.stmt("# patternProperties")
                with m.for_("rx, visitor in self._pattern_properties_regexes"):
                    with m.for_("k, v in d.items()"):
                        m.stmt("m = rx.search(rx)")
                        with m.if_("m is not None and visitor is not None"):
                            m.stmt("ctx.run(k, visitor.visit, v)")
            if self.helper.has_additional_properties(ev):
                m.sep()
                m.stmt("# additionalProperties")

                def _on_continue():
                    m.stmt("continue")

                if ev.data["additionalProperties"] is False:

                    def _on_continue_with_warning():
                        # m.stmt(f"raise RuntimeError('additionalProperties is False, but unexpected property is found (k=%s, where=%s)' %  (k, self.__class__.__name__))")
                        self.logging.log(
                            m,
                            "logger.warning('unexpected property is found: %r, where=%s', k, self.__class__.__name__)",
                        )
                        m.stmt("continue")

                    _on_continue = _on_continue_with_warning  # noqa

                with m.for_("k, v in d.items()"):
                    with m.if_("if k in self._properties"):
                        m.stmt("continue")
                    if self.helper.has_pattern_properties(ev):
                        with m.for_("rx, visitor in self._pattern_properties_regexes"):
                            m.stmt("m = rx.search(rx)")
                            with m.if_("m is not None"):
                                m.stmt("continue")

                    if ev.data["additionalProperties"] is False:
                        self.logging.log(
                            m,
                            "logger.warning('unexpected property is found: %r, where=%s', k, self.__class__.__name__)",
                        )
                    else:
                        m.stmt("ctx.run(k, self.additional_properties.visit, v)")

    def _gen_properties_visitors(self, ev: Event, *, m) -> None:
        for name, ref in self.helper.iterate_links(ev):
            m.stmt("@reify  # visitor")
            with m.def_(name, "self"):
                lazy_link_name = self.name_manager.create_lazy_visitor_name(ref)
                self.logging.log(
                    m,
                    """logger.debug("resolve node: %s", {cls!r})""",
                    cls=lazy_link_name,
                )
                m.stmt("return {cls}()", cls=lazy_link_name)

    def _gen_xxx_of_visitors(self, ev: Event, *, m) -> None:
        for i, ref in self.helper.iterate_xxx_of_links(ev):
            name = f"{ev.name}{i}"
            m.stmt(f"@reify  # visitor")
            with m.def_(name, "self"):
                if ref is None:
                    m.return_("None")
                    continue

                lazy_link_name = self.name_manager.create_lazy_visitor_name(ref)
                self.logging.log(
                    m,
                    """logger.debug("resolve {name} node: %s", {cls!r})""",
                    name=name,
                    cls=lazy_link_name,
                )
                m.stmt("return {cls}()", cls=lazy_link_name)


def main():
    from dictknife.swaggerknife.stream import main

    m = Module(import_unique=True)
    m.import_area = m.submodule()
    m.sep()

    g = Generator(m)
    definitions = {}
    toplevels: t.List[Event] = []

    stream: t.Iterable[Event] = main(create_visitor=ToplevelVisitor)
    for ev in stream:
        if names.roles.has_expanded in ev.roles:
            definitions.update(
                ev.get_annotated(names.annotations.expanded)["definitions"]
            )
        if names.roles.toplevel_properties in ev.roles:
            toplevels.append(ev)
            continue
        if names.roles.has_name in ev.roles:
            g.generate_class(ev)

    for ev in toplevels:
        if ev.uid.endswith("#/"):
            g.generate_class(ev, clsname="toplevel")

    if definitions:
        m.import_area.from_("dictknife.swaggerknife.stream", "runtime")
        data = {"definitions": definitions}
        g.emitter.emit_data(m, "_case = runtime.Case({})", data, nofmt=True)

    print(m)


if __name__ == "__main__":
    main()
