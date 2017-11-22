from functools import partial
from . import csv

load = partial(csv.load, delimiter="\t")
dump = partial(csv.dump, delimiter="\t")

