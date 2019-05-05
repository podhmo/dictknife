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


# todo: toplevel properties
# todo: anonymous definition(nested definition)
# todo: pattern properties, additionalProperties


class Generator:
    def __init__(self, m=None, logging_enable=True):
        self.logging_enable = logging_enable
        self.m = m or Module(import_unique=True)
        self.visitors = {}

        # xxx:
        if self.logging_enable:
            self.m.from_("logging", "getLogger")
            self.m.stmt("logger = getLogger(__name__)  # noqa")

    def _iterate_links(self, ev: Event) -> t.Iterable[t.Tuple[str, str]]:
        if names.predicates.has_links not in ev.predicates:
            return []
        return ev.get_annotated(names.annotations.links)

    def _register_visitor(self, ev: Event, clsname: str) -> None:
        self.visitors[ev.uid] = clsname

    def _gen_logging(self, m, fmt, *args, **kwargs):
        if self.logging_enable:
            m.stmt(fmt, *args, **kwargs)

    def has_pattern_properties(self, ev: Event) -> bool:
        return (
            names.predicates.has_extra_properties in ev.predicates
            and "patternProperties" in ev.data
        )

    def has_additional_properties(self, ev: Event) -> bool:
        return (
            names.predicates.has_extra_properties in ev.predicates
            and "additionalProperties" in ev.data
        )

    def gen_pattern_properties_regexes(self, ev: Event, *, m=None) -> None:
        m = self.m
        m.stmt("@reify  # visitor")
        with m.def_("_pattern_properties_regexes", "self"):
            m.import_("re")
            m.stmt("r = []")
            for k, ref in ev.get_annotated(names.annotations.pattern_properties_links):
                if ref is None:
                    m.stmt("""r.append((re.compile({k!r}), None))""", k=k)
                    continue

                def to_str(ref: str = ref):
                    name = self.visitors[ref]
                    # name = self.visitors.get(ref) or "<missing>"
                    logger.debug("resolve clasname: %s -> %s", ref, name)
                    return name

                visitor_cls = _LazyName(to_str)
                m.stmt(
                    """r.append((re.compile({k!r}), {cls}()))""", k=k, cls=visitor_cls
                )
            m.return_("r")
            # m.return_(
            #     """[(re.compile(k), k) for self._extra_properties["patternProperties"]]"""
            # )

    def gen_visitor(self, ev: Event, *, m=None, clsname: str = None) -> None:
        m = self.m
        clsname = pascalcase(clsname or ev.get_annotated(names.annotations.name))
        self._register_visitor(ev, clsname)

        m.from_("dictknife.swaggerknife.stream", "Visitor")

        with m.class_(clsname, "Visitor"):
            m.stmt(f"schema_type = {ev.name!r}")
            m.stmt(f"predicates = {ev.predicates!r}")

            m.stmt(f"_uid = {ev.uid!r}")
            if names.predicates.has_properties in ev.predicates:
                m.stmt(
                    f"_properties = {ev.get_annotated(names.annotations.properties)!r}"
                )
            if names.predicates.has_extra_properties in ev.predicates:
                m.stmt(
                    "_extra_properties = {!r}",
                    json.loads(
                        json.dumps(ev.get_annotated(names.annotations.extra_properties))
                    ),
                )
            m.sep()

            if self.has_pattern_properties(ev):
                self.gen_pattern_properties_regexes(ev, m=m)

            m.stmt("@reify")
            with m.def_("node", "self"):
                with m.try_():
                    self._gen_logging(
                        m, f"""logger.debug("resolve node: %s", {clsname!r})"""
                    )
                    m.submodule().from_(".nodes", clsname)
                    m.return_("{}()", clsname)
                with m.except_("ImportError"):
                    self._gen_logging(
                        m,
                        f"""logger.info("resolve node: %s is not found", {clsname!r})""",
                    )
                    m.return_("None")

            with m.def_("__call__", "self", "ctx: Context", "d: dict"):
                if ev.name == names.types.array:
                    m.return_("[self._visit(ctx, x) for x in d]")
                elif names.predicates.primitive_type in ev.predicates:
                    # drop schema definitions?
                    m.return_("self._visit(ctx, d)  # todo: simplify")
                else:
                    m.return_("self._visit(ctx, d)  # todo: remove this code")

            with m.def_("_visit", "self", "ctx: Context", "d: dict"):
                self._gen_logging(m, f"""logger.debug("visit: %s", {clsname!r})""")

                with m.if_("self.node is not None"):
                    m.stmt("self.node.attach(ctx, d, self)")

                for name, ref in self._iterate_links(ev):
                    with m.if_(f"{name!r} in d"):
                        m.stmt(
                            f"ctx.run({name!r}, self.{name}.visit, d[{name!r}])",
                            name=name,
                        )

                if self.has_pattern_properties(ev):
                    m.sep()
                    m.stmt("# patternProperties")
                    with m.for_("rx, visitor in self._pattern_properties_regexes"):
                        with m.for_("k, v in d.items()"):
                            m.stmt("m = rx.search(rx)")
                            with m.if_("m is not None and visitor is not None"):
                                m.stmt("ctx.run(k, visitor.visit, v)")
                if self.has_additional_properties(ev):
                    m.sep()
                    m.stmt("# additionalProperties")

                    def _on_continue():
                        m.stmt("continue")

                    if ev.data["additionalProperties"] is False:

                        def _on_continue_with_warning():
                            # m.stmt(f"raise RuntimeError('additionalProperties is False, but unexpected property is found (k=%s, where=%s)' %  (k, self.__class__.__name__))")
                            self._gen_logging(
                                m,
                                "logger.warning('unexpected property is found: %r, where=%s', k, self.__class__.__name__)",
                            )
                            m.stmt("continue")

                        _on_continue = _on_continue_with_warning  # noqa

                    with m.for_("k, v in d.items()"):
                        with m.if_("if k in self._properties"):
                            m.stmt("continue")
                        if self.has_pattern_properties(ev):
                            with m.for_(
                                "rx, visitor in self._pattern_properties_regexes"
                            ):
                                m.stmt("m = rx.search(rx)")
                                with m.if_("m is not None"):
                                    m.stmt("continue")

                        if ev.data["additionalProperties"] is False:
                            self._gen_logging(
                                m,
                                "logger.warning('unexpected property is found: %r, where=%s', k, self.__class__.__name__)",
                            )
                        else:
                            m.stmt("ctx.run(k, self.additional_properties.visit, v)")

            for name, ref in self._iterate_links(ev):
                m.stmt("@reify  # visitor")
                with m.def_(name, "self"):

                    def to_str(ref: str = ref):
                        name = self.visitors[ref]
                        # name = self.visitors.get(ref) or "<missing>"
                        logger.debug("resolve clasname: %s -> %s", ref, name)
                        return name

                    lazy_link_name = _LazyName(to_str)
                    self._gen_logging(
                        m,
                        """logger.debug("resolve node: %s", {cls!r})""",
                        cls=lazy_link_name,
                    )
                    m.stmt("return {cls}()", cls=lazy_link_name)


def main():
    from dictknife.swaggerknife.stream import main

    g = Generator()
    toplevels: t.List[Event] = []

    stream: t.Iterable[Event] = main(create_visitor=ToplevelVisitor)
    for ev in stream:
        if names.predicates.toplevel_properties in ev.predicates:
            toplevels.append(ev)
            continue
        if names.predicates.has_name in ev.predicates:
            g.gen_visitor(ev)

    for ev in toplevels:
        if ev.uid.endswith("#/"):
            g.gen_visitor(ev, clsname="toplevel")
    print(g.m)


if __name__ == "__main__":
    main()
