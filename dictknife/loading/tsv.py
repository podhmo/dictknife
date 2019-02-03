from functools import partial
from . import csv

setup_parser = csv.setup_parser
load = partial(csv.load, delimiter="\t")
dump = partial(csv.dump, delimiter="\t")
