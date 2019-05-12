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


# todo: toplevel $ref
# todo: drop link of primitive types
# todo: required support
# todo: enum support(?)
# todo: additionalProperties (schema)
# todo: anonymous definition(nested definition)
# todo: anonymous patternPropertites
# todo: anonymous definition(oneOf, anyof, allOf)
# todo: rename python reserved word


class Helper:
    def classname(self, ev: Event, *, name: str = None) -> str:
        return pascalcase(name or ev.get_annotated(names.annotations.name))

    def create_submodule(self, m) -> Module:
        sm = m.submodule()
        sm.import_area = m.import_area
        return sm

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
        return ev.get_annotated(names.annotations.links) or []

    def iterate_xxx_of_links(self, ev: Event) -> t.Iterable[t.Tuple[str, str]]:
        return ev.get_annotated(names.annotations.xxx_of_links) or []


class NameManager:  # todo: rename
    def __init__(self):
        self.visitors = {}

    def register_visitor_name(self, ev: Event, clsname):
        self.visitors[ev.uid] = clsname

    def create_lazy_visitor_name(self, uid: str) -> _LazyName:
        def to_str(uid: str = uid):
            # name = self.visitors[uid]
            name = self.visitors.get(uid) or "<missing>"
            logger.debug("resolve clasname: %s -> %s", uid, name)
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

        # xxx:
        self.registered = {}  # uid -> classname
        self._end_of_private_visit_method_conts = {}  # classname -> m.submodule()
        self._end_of_class_definition_conts = {}  # classname -> m.submodule()

    def generate_class(self, ev: Event, *, m=None, clsname: str = None) -> None:
        m = m or self.m
        clsname = clsname or self.helper.classname(ev)
        self.registered[ev.uid] = clsname
        self.name_manager.register_visitor_name(ev, clsname)

        m.import_area.from_("dictknife.swaggerknife.stream.interfaces", "Visitor")
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

            # xxx:
            self._end_of_class_definition_conts[clsname] = self.helper.create_submodule(
                m
            )

    def _gen_headers(self, ev: Event, *, m) -> None:
        m.stmt(f"_schema_type = {ev.name!r}")
        m.stmt(f"_roles = {sorted(ev.roles)!r}")

        m.stmt(f"_uid = {ev.uid!r}")
        if names.roles.has_properties in ev.roles:
            m.stmt(
                f"_properties = {sorted(ev.get_annotated(names.annotations.properties))!r}"
            )
        if names.roles.has_extra_properties in ev.roles:
            data = ev.get_annotated(names.annotations.extra_properties)
            self.emitter.emit_data(m, "_extra_properties = {}", sorted(data))

        links = list(self.helper.iterate_links(ev))
        if links:
            m.stmt(
                f"_links = {[name for name, ref in self.helper.iterate_links(ev)]!r}"
            )
        if names.roles.combine_type in ev.roles:
            self.emitter.emit_data(
                m,
                "_xxx_of_definitions = {}",
                ev.get_annotated(names.annotations.expanded)[ev.name],
                nofmt=False,
            )
        m.sep()

    def _gen_pattern_properties_regexes(self, ev: Event, *, m) -> None:
        m.stmt("@reify")
        with m.def_("_pattern_properties_regexes", "self"):
            m.import_("re")
            m.stmt("return [")
            with m.scope():
                for k, uid in ev.get_annotated(
                    names.annotations.pattern_properties_links
                ):
                    if uid is None:
                        uid = f"{ev.uid}/{k}"  # xxx

                    lazy_name = self.name_manager.create_lazy_visitor_name(uid)
                    m.stmt(
                        """(re.compile({k!r}), resolve_visitor({k!r}, cls={cls}, logger=logger)),""",
                        k=k,
                        cls=lazy_name,
                    )
            m.stmt("]")

    def _gen_node_property(self, ev: Event, *, clsname, m) -> None:
        m.import_area.from_("dictknife.swaggerknife.stream", "runtime")
        m.stmt("@reify")
        with m.def_("node", "self"):
            m.stmt(
                "return runtime.resolve_node({path!r}, here=__name__, logger=logger)",
                path=f".nodes.{clsname}",
            )

    def _gen_visit_method(self, ev: Event, *, m) -> None:
        with m.def_("visit", "self", "ctx: Context", "d: dict"):
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
                    for i, prop in enumerate(bodies[ev.name]):
                        with m.if_(f"_case.when(d, {prop['$ref']!r})"):
                            ref = links[i]
                            if ref is None:
                                m.stmt("return  # not supported yet")
                                continue  # xxx
                            else:
                                m.stmt(
                                    f"return ctx.run(None, self.{ev.name}{i!r}.visit, d)"
                                )
                    m.stmt(
                        "raise ValueError('unexpected value')  # todo gentle message"
                    )
                elif ev.name == names.types.anyOf:
                    m.stmt("matched = False")
                    for i, prop in enumerate(bodies[ev.name]):
                        with m.if_(f"_case.when(d, {prop['$ref']!r})"):
                            ref = links[i]
                            if ref is None:
                                m.stmt("pass  # not supported yet")
                                continue  # xxx
                            else:
                                m.stmt("matched = True")
                                m.stmt(f"ctx.run(None, self.{ev.name}{i!r}.visit, d)")
                    with m.if_("not matched"):
                        m.stmt(
                            "raise ValueError('unexpected value')  # todo gentle message"
                        )
                elif ev.name == names.types.allOf:
                    for i, prop in enumerate(bodies[ev.name]):
                        with m.if_(f"not _case.when(d, {prop['$ref']!r})"):
                            m.stmt(
                                "raise ValueError('unexpected value')  # todo gentle message"
                            )
                        ref = links[i]
                        if ref is None:
                            m.stmt("pass  # not supported yet")
                            continue  # xxx
                        else:
                            m.stmt(f"ctx.run(None, self.{ev.name}{i!r}.visit, d)")
            else:
                m.return_("self._visit(ctx, d)  # todo: remove this code")

    def _gen_visit_private_method(self, ev: Event, *, clsname: str, m) -> None:
        with m.def_("_visit", "self", "ctx: Context", "d: dict"):
            self.logging.log(m, f"""logger.debug("visit: %s", {clsname!r})""")

            with m.if_("self.node is not None"):
                m.stmt("self.node.attach(ctx, d, self)")

            for name, uid in self.helper.iterate_links(ev):
                if uid is None:
                    uid = f"{ev.uid}/{name}"
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

            # add code, after visited
            self._end_of_private_visit_method_conts[
                clsname
            ] = self.helper.create_submodule(m)

    def _gen_visitor_property(
        self, ev: Event, *, name: str, uid: str, m, prefix: str = ""
    ) -> None:
        m.import_area.from_("dictknife.swaggerknife.stream", "runtime")
        m.stmt("@reify")
        with m.def_(name, "self"):
            lazy_link_name = self.name_manager.create_lazy_visitor_name(uid)
            m.stmt(
                "return runtime.resolve_visitor({name!r}, cls={prefix}{cls}, logger=logger)",
                name=name,
                cls=lazy_link_name,
                prefix=prefix,
            )

    def _gen_properties_visitors(self, ev: Event, *, m) -> None:
        for name, uid in self.helper.iterate_links(ev):
            if uid is None:
                continue  # generated by delayed stream
            self._gen_visitor_property(ev, name=name, uid=uid, m=m)

    def _gen_xxx_of_visitors(self, ev: Event, *, m) -> None:
        for i, uid in self.helper.iterate_xxx_of_links(ev):
            name = f"{ev.name}{i}"
            self._gen_visitor_property(ev, name=name, uid=uid, m=m)


def main():
    from dictknife.swaggerknife.stream import main

    m = Module(import_unique=True)
    m.header_area = m.submodule()
    m.import_area = m.submodule()
    m.sep()

    g = Generator(m)
    definitions = {}
    toplevels: t.List[Event] = []

    stream: t.Iterable[Event] = main(create_visitor=ToplevelVisitor)

    def consume_stream(stream: t.Iterable[Event], *, is_delayed=False) -> t.List[Event]:
        delayed_stream: t.List[Event] = []
        for ev in stream:
            if ev.uid in g.registered:
                continue

            if names.roles.has_expanded in ev.roles:
                definitions.update(
                    ev.get_annotated(names.annotations.expanded)["definitions"]
                )
            if names.roles.has_name in ev.roles:
                g.generate_class(ev)
                continue

            if not is_delayed:
                if names.roles.toplevel_properties in ev.roles:
                    toplevels.append(ev)  # xxx
                delayed_stream.append(ev)
                continue

            # xxx:
            if (
                ev.name in (names.types.object, names.types.array)
                or names.roles.combine_type in ev.roles
            ):
                uid_and_clsname_pairs = sorted(
                    g.registered.items(), key=lambda pair: len(pair[0]), reverse=True
                )

                for parent_uid, parent_clsname in uid_and_clsname_pairs:
                    uid = ev.uid
                    if uid.startswith(parent_uid):
                        classdef_sm = g._end_of_class_definition_conts[parent_clsname]
                        fieldname = uid.replace(parent_uid, "").lstrip("/")
                        clsname = f"_{g.helper.classname(ev, name=fieldname)}"

                        classdef_sm.stmt(
                            f"# anonymous definition for {fieldname!r} (TODO: nodename)"
                        )
                        g.generate_class(ev, clsname=clsname, m=classdef_sm)

                        # ok: properties
                        # todo: additionalProperties, patternProperties
                        # todo:  oneOf, anyof, allof
                        # assert "/" not in fieldname
                        name = fieldname
                        g._gen_visitor_property(
                            ev,
                            name=name,
                            uid=uid,
                            prefix=f"{parent_clsname}.",
                            m=classdef_sm,
                        )
                        break
                else:
                    raise RuntimeError(f"unexpected type: {ev.name}")
        return delayed_stream

    delayed_stream = consume_stream(stream, is_delayed=False)

    for ev in toplevels:
        if ev.uid.endswith("#/"):
            g.generate_class(ev, clsname="Toplevel")

    import os.path

    m.header_area.stmt(
        f"# generated from {os.path.relpath(ev.root_file, start=os.getcwd())}"
    )
    m.import_area.from_("dictknife.langhelpers", "reify")
    m.import_area.from_("dictknife.swaggerknife.stream", "runtime")
    m.import_area.from_("dictknife.swaggerknife.stream.context", "Context")

    delayed_stream = sorted(delayed_stream, key=lambda ev: len(ev.uid))
    consume_stream(delayed_stream, is_delayed=True)

    if definitions:
        data = {"definitions": definitions}
        g.emitter.emit_data(m, "_case = runtime.Case({})", data, nofmt=True)

    print(m)


if __name__ == "__main__":
    main()
