from functools import partial
from . import csv
from .raw import setup_parser

load = partial(csv.load, delimiter="\t")
dump = partial(csv.dump, delimiter="\t")
