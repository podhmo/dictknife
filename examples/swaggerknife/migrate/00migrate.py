import logging
from dictknife.jsonknife import get_resolver
from dictknife.swaggerknife.migration import Migration


def run(*, src: str, savedir: str, log: str, dry_run: bool = False) -> None:
    logging.basicConfig(level=log)

    resolver = get_resolver(src)
    with Migration(resolver).migrate(dry_run=dry_run, keep=True, savedir=savedir) as u:
        for k, item in u.iterate_items():
            if k == "definitions/person":
                ref = "#/definitions/person/properties/value"
                u.update(item.resolver, ref, {"type": "integer"})
            if k == "definitions/name":
                ref = "#/definitions/name/description"
                u.update(item.resolver, ref, "name of something")


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
