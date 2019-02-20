import logging
from functools import partial
from dictknife import DictWalker
from dictknife.accessing import Scope
from dictknife.langhelpers import make_dict
from dictknife.transform import normalize_dict
from dictknife.jsonknife import get_resolver
from dictknife.swaggerknife.migration import Migration, is_empty_collection

# todo: update ref
# todo: move definitions
# todo: support parameters


# reorder
def transform(doc, *, sort_keys=False):
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
        r = normalize_dict(r)  # side effect
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
    frame = {}
    if "parameters" in data:
        if isinstance(data["parameters"], (list, tuple)):
            itr = enumerate(data["parameters"])
        else:
            itr = data["parameters"].items()

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

                frame["requestBody"] = request_body
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


def migrate_refs(uu, *, scope, walker=DictWalker(["$ref"])):
    for path, d in walker.walk(uu.resolver.doc):
        if "/definitions/" in d["$ref"]:
            uu.update_by_path(
                path, d["$ref"].replace("/definitions/", "/components/schemas/", 1)
            )


def migrate_for_subfile(uu, *, scope, schema_walker=DictWalker(["schema"])):
    migrate_refs(uu, scope=scope)
    if uu.has("definitions"):
        uu.update_by_path(["components", "schemas"], uu.pop_by_path(["definitions"]))
    if uu.has("securityDefinitions"):
        uu.update_by_path(
            ["components", "securitySchemas"], uu.pop_by_path(["securityDefinitions"])
        )
    frame = {}
    frame.update(
        migrate_parameters(uu, uu.resolver.doc, path=["parameters"], scope=scope)
    )
    with scope.scope(frame or None):
        if uu.has("paths"):
            for url_path, path_item in uu.resolver.doc["paths"].items():
                # xxx: vendor extensions?
                if url_path.startswith("x-"):
                    continue

                # todo: parse pathItem object
                # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#path-item-object
                operation_methods = [
                    "get",
                    "put",
                    "post",
                    "delete",
                    "options",
                    "head",
                    "patch",
                ]
                frame = {}
                frame.update(
                    migrate_parameters(
                        uu,
                        path_item,
                        path=["paths", url_path, "parameters"],
                        scope=scope,
                    )
                )
                with scope.scope(frame or None):
                    for method_name in operation_methods:
                        operation = path_item.get(method_name)
                        if operation is None:
                            continue

                        # todo: parse Operation object
                        # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object

                        frame = {}

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
                                for spath, sd in schema_walker.walk(
                                    operation["responses"]
                                ):
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
                                    uu.update_by_path(
                                        [*fullpath[:-1], "content"], content
                                    )


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
        migrate_for_mainfile(u, scope=scope)
        # todo: parse toplevel parameters
        for resolver in u.resolvers:
            uu = u.new_child(resolver)
            migrate_for_subfile(uu, scope=scope)


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
