from dictknife import loading


def run():
    sheet = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms#/Class Data!A1:E'
    result = loading.loadfile(sheet, format="spreadsheet")
    loading.dumpfile(result, format="json")


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    args = parser.parse_args(argv)
    run(**vars(args))


if __name__ == '__main__':
    main()
