default: 00 01 02 03 04 05 06 07 08

00:
	dictknife shape 00*.json > $@.output
01:
	dictknife shape 01*.json > $@.output
02:
	dictknife shape 01*.json --squash > $@.output
03:
	dictknife shape 02*.json --skiplist > $@.output
04:
	dictknife shape 02*.json --skiplist > $@.output
05:
	dictknife shape 03*.json --skiplist > $@.output
06:
	dictknife shape 03*.json --skiplist > $@.output
07:
	cat 03*.json | dictknife shape -i json --skiplist > $@.output
08:
	cat 03*.json | dictknife shape -i json --skiplist 00*.json 01*.json > $@.output
