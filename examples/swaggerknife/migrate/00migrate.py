import logging
from dictknife.jsonknife import get_resolver
from dictknife.swaggerknife.migration import Migration


def run(*, src: str, savedir: str, log: str, dry_run: bool = False) -> None:
    logging.basicConfig(level=getattr(logging, log))

    resolver = get_resolver(src)
    # xxx: sort_keys for ambitious output (for 3.6 only?)
    with Migration(resolver, dump_options={"sort_keys": True}).migrate(
        dry_run=dry_run, keep=True, savedir=savedir
    ) as u:
        for k, item in u.iterate_items():
            if k == "definitions/person":
                ref = "#/definitions/person/properties/value"
                u.update(ref, {"type": "integer"}, resolver=item.resolver)
            if k == "definitions/name":
                ref = "#/definitions/name/description"
                u.update(ref, "name of something", resolver=item.resolver)


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("--log", default="DEBUG")
    parser.add_argument("--src", required=True)
    parser.add_argument("--savedir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    run(**vars(args))


if __name__ == "__main__":
    main()
