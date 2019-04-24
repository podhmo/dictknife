from dictknife.swaggerknife.stream import run

if __name__ == "__main__":
    import argparse
    import logging

    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("--log", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log))
    run(args.src)
