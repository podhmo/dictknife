import logging
import itertools
from functools import partial

from dictknife import DictWalker
from dictknife.accessing import Scope
from dictknife.langhelpers import make_dict
from dictknife.transform import str_dict
from dictknife.jsonknife import get_resolver
from dictknife.swaggerknife.migration import Migration, is_empty_collection, is_empty

logger = logging.getLogger(__name__)


def transform(doc, *, sort_keys=False):
    """reorder"""
    heavy_defs = ["definitions", "schemas", "responses", "parameters", "paths"]
    r = make_dict()
    for k, v in doc.items():
        if k in heavy_defs:
            continue
        r[k] = v
    for k in heavy_defs:
        if k in doc:
            r[k] = doc[k]
    if sort_keys:
        r = str_dict(r)  # side effect
    return r


def migrate_for_mainfile(u, *, scope):
    if u.has("swagger"):
        u.pop("swagger")
        u.update("openapi", "3.0.0")

    if u.has("host"):
        url = u.pop("host")
        if u.has("basePath"):
            base_path = u.pop("basePath")
            url = "{}/{}".format(url.rstrip("/"), base_path.lstrip("/"))
        description = ""

        schemas = ["http"]
        if u.has("schemes"):
            schemas = u.pop("schemes")
        servers = []
        for schema in schemas:
            server = u.make_dict()
            server["url"] = "{}://{}".format(schema.rstrip(":/"), url)
            server["description"] = description
            servers.append(server)
        u.update("/servers", servers)

    if u.has("produces"):
        scope.push({"produces": u.pop("produces")})
    if u.has("consumes"):
        scope.push({"consumes": u.pop("consumes")})


def migrate_parameters(uu, data, *, path, scope):
    frame = make_dict()
    if "parameters" in data:
        if isinstance(data["parameters"], (list, tuple)):
            itr = enumerate(data["parameters"])
        elif hasattr(data["parameters"], "items"):
            itr = data["parameters"].items()
        elif is_empty(data["parameters"]):
            return frame
        else:
            raise RuntimeError(
                "unexpected #/parameters: %{!r}".format(data["parameters"])
            )

        for i, param in itr:
            if "$ref" in param:
                continue

            in_value = param.get("in")

            if in_value in ("body", "form"):
                param = uu.pop_by_path([*path, i])
                content = uu.make_dict()

                for k, v in param.items():
                    if k in {
                        "name",
                        "in",
                        "description",
                        "required",
                        "collectionFormat",
                    }:
                        continue
                    # xxx: vendor extensions?
                    content[k] = v

                request_body = uu.make_dict()
                if "description" in param:
                    request_body["description"] = param["description"]
                request_body["required"] = param.get("required", True)  # default: true
                if in_value == "body":
                    consume = "application/json"
                elif in_value == "form":
                    consume = "application/x-www-form-urlencoded"
                request_body["content"] = {consume: content}

                # xxx:
                frame[i if hasattr(i, "upper") else "requestBody"] = request_body
            else:
                content = uu.make_dict()
                for k in list(param.keys()):
                    if k in {
                        "name",
                        "in",
                        "description",
                        "required",
                        "collectionFormat",
                    }:
                        continue
                    content[k] = uu.pop_by_path([*path, i, k])
                uu.update_by_path([*path, i, "schema"], content)
        if is_empty_collection(data["parameters"]):
            uu.pop_by_path(path)
    return frame


def migrate_refs(uu, data, *, scope, walker=DictWalker(["$ref"])):
    for path, d in walker.walk(data):
        if "/definitions/" in d["$ref"]:
            uu.update_by_path(
                path, d["$ref"].replace("/definitions/", "/components/schemas/", 1)
            )
        if "/parameters/" in d["$ref"]:
            uu.update_by_path(
                path, d["$ref"].replace("/parameters/", "/components/parameters/", 1)
            )

        if "/responses/" in d["$ref"]:
            uu.update_by_path(
                path, d["$ref"].replace("/responses/", "/components/responses/", 1)
            )


def migrate_paths(uu, data, *, scope, schema_walker=DictWalker(["schema"])):
    for url_path, path_item in data["paths"].items():
        # xxx: vendor extensions?
        if url_path.startswith("x-"):
            continue

        # todo: parse pathItem object
        # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#path-item-object
        operation_methods = ["get", "put", "post", "delete", "options", "head", "patch"]
        frame = make_dict()
        frame.update(
            migrate_parameters(
                uu, path_item, path=["paths", url_path, "parameters"], scope=scope
            )
        )
        with scope.scope(frame or None):
            for method_name in operation_methods:
                operation = path_item.get(method_name)
                if operation is None:
                    continue

                # todo: parse Operation object
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object

                frame = make_dict()

                # parameters
                frame.update(
                    migrate_parameters(
                        uu,
                        operation,
                        path=["paths", url_path, method_name, "parameters"],
                        scope=scope,
                    )
                )

                # produces
                if "produces" in operation:
                    frame["produces"] = uu.pop_by_path(
                        ["paths", url_path, method_name, "produces"]
                    )
                # consumes
                if "consumes" in operation:
                    frame["consumes"] = uu.pop_by_path(
                        ["paths", url_path, method_name, "consumes"]
                    )

                # responses
                with scope.scope(frame or None):
                    # requestBody
                    request_body = scope.get(["requestBody"])
                    if request_body is not None:
                        uu.update_by_path(
                            ["paths", url_path, method_name, "requestBody"],
                            request_body,
                        )

                    if "responses" in operation:
                        for spath, sd in schema_walker.walk(operation["responses"]):
                            fullpath = [
                                "paths",
                                url_path,
                                method_name,
                                "responses",
                                *spath,
                            ]
                            schema = uu.pop_by_path(fullpath)
                            content = uu.make_dict()
                            for produce in scope[["produces"]]:
                                content[produce] = {"schema": schema}
                            uu.update_by_path([*fullpath[:-1], "content"], content)


def migrate_for_subfile(uu, *, scope, callbacks, ref_wawlker=DictWalker(["$ref"])):
    migrate_refs(uu, uu.resolver.doc, scope=scope)
    if uu.has("definitions"):
        uu.update_by_path(["components", "schemas"], uu.pop_by_path(["definitions"]))
    if uu.has("parameters"):
        request_bodies = migrate_parameters(
            uu, uu.resolver.doc, path=["parameters"], scope=scope
        )
        uu.update_by_path(["components", "parameters"], uu.pop_by_path(["parameters"]))
        # for in:body
        if request_bodies:
            names = list(request_bodies.keys())

            # todo: optimizatin?
            def fixref(uu, *, names=names):
                will_be_remove_paths_if_empty = set()
                for path, sd in ref_wawlker.walk(uu.resolver.doc):
                    ref = sd["$ref"]
                    if is_empty(ref):
                        continue
                    if "#/components/parameters" not in ref:
                        continue
                    if not any(name in ref for name in names):
                        continue
                    uu.pop_by_path(path[:-1])
                    new_value = {
                        "$ref": ref.replace(
                            "#/components/parameters", "#/components/requestBodies"
                        )
                    }
                    if path[0] == "paths":
                        new_path = itertools.takewhile(
                            lambda x: x != "parameters", path
                        )
                        uu.update_by_path([*new_path, "requestBody"], new_value)
                    elif path[0] == "components":
                        # #/components/parameters/<name>
                        uu.update_by_path(
                            ["components", "requestBodies", path[2]], new_value
                        )
                    else:
                        raise RuntimeError("unexpected path: {}".format(path))

                    will_be_remove_paths_if_empty.add(tuple(path[:-2]))

                for path in will_be_remove_paths_if_empty:
                    if is_empty_collection(uu.resolver.access(path)):
                        uu.pop_by_path(path)

            callbacks.append(fixref)

            for name, body in request_bodies.items():
                uu.update_by_path(["components", "requestBodies", name], body)

    if uu.has("responses"):
        uu.update_by_path(["components", "responses"], uu.pop_by_path(["responses"]))
    if uu.has("securityDefinitions"):
        uu.update_by_path(
            ["components", "securitySchemes"], uu.pop_by_path(["securityDefinitions"])
        )

    # todo: requestBodies
    frame = make_dict()
    frame.update(
        migrate_parameters(uu, uu.resolver.doc, path=["parameters"], scope=scope)
    )

    with scope.scope(frame or None):
        if uu.has("paths"):
            migrate_paths(uu, uu.resolver.doc, scope=scope)


# todo: skip x-XXX
def run(
    *, src: str, savedir: str, dry_run: bool = False, sort_keys: bool = False
) -> None:

    resolver = get_resolver(src)
    # xxx: sort_keys for ambitious output (for 3.6 only?)
    # xxx: sort_keys=True, TypeError is occured, compare between str and int
    # xxx: transform set by dump_options?
    m = Migration(
        resolver,
        dump_options={"sort_keys": sort_keys},
        transform=partial(transform, sort_keys=sort_keys),
    )
    with m.migrate(dry_run=dry_run, keep=True, savedir=savedir) as u:
        scope = Scope(
            {"consumes": ["application/json"], "produces": ["application/json"]}
        )
        callbacks = []
        logger.debug("migrate mainfile file=%s", u.name)
        migrate_for_mainfile(u, scope=scope)
        for resolver in u.resolvers:
            uu = u.new_child(resolver)
            logger.debug("migrate subfile file=%s", uu.name)
            migrate_for_subfile(uu, scope=scope, callbacks=callbacks)

        # callback
        logger.debug("callbacks callbacks=%s", len(callbacks))
        for resolver in u.resolvers:
            uu = u.new_child(resolver)
            for cb in callbacks:
                cb(uu)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("--logging", default="DEBUG")
    parser.add_argument("--src", required=True)
    parser.add_argument("--savedir")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sort-keys", action="store_true")  # drop in the end
    args = parser.parse_args(argv)
    params = vars(args)
    logging.basicConfig(level=getattr(logging, params.pop("logging")))
    run(**params)


if __name__ == "__main__":
    main()
