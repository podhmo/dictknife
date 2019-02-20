import logging
from functools import partial
from dictknife.accessing import Scope
from dictknife.langhelpers import make_dict
from dictknife.transform import normalize_dict
from dictknife.jsonknife import get_resolver, path_to_json_pointer
from dictknife.swaggerknife.migration import Migration

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


def migrate_for_subfile(u, *, scope):
    from dictknife import DictWalker

    schema_walker = DictWalker(["schema"])

    for resolver in u.resolvers:
        uu = u.new_child(resolver)
        if uu.has("paths", resolver=resolver):
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
                for method_name in operation_methods:
                    operation = path_item.get(method_name)
                    if operation is None:
                        continue

                    # todo: parse Operation object
                    # https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object

                    # parameters
                    frame = {}
                    if "produces" in operation:
                        ref = path_to_json_pointer(
                            ["paths", url_path, method_name, "produces"]
                        )
                        frame["produces"] = uu.pop(ref)

                    # responses
                    with scope.scope(frame or None):
                        if "responses" in operation:
                            for spath, sd in schema_walker.walk(operation["responses"]):
                                fullpath = [
                                    "paths",
                                    url_path,
                                    method_name,
                                    "responses",
                                    *spath,
                                ]
                                ref = path_to_json_pointer(fullpath)
                                schema = uu.pop(ref)
                                content = uu.make_dict()
                                for produce in scope[["produces"]]:
                                    content[produce] = {"schema": schema}
                                ref = path_to_json_pointer([*fullpath[:-1], "content"])
                                uu.update(ref, content)


# todo: skip x-XXX
def run(
    *, src: str, savedir: str, log: str, dry_run: bool = False, sort_keys: bool = False
) -> None:
    logging.basicConfig(level=getattr(logging, log))

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
        scope = Scope()
        migrate_for_mainfile(u, scope=scope)
        migrate_for_subfile(u, scope=scope)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("--log", default="DEBUG")
    parser.add_argument("--src", required=True)
    parser.add_argument("--savedir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sort-keys", action="store_true")  # drop in the end
    args = parser.parse_args(argv)
    run(**vars(args))


if __name__ == "__main__":
    main()
