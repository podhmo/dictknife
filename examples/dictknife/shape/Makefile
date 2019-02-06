default: 00 01 02 03 04 05 06 07 08

00:
	dictknife shape src/00*.json > dst/$@.output
01:
	dictknife shape src/01*.json > dst/$@.output
02:
	dictknife shape src/01*.json --squash > dst/$@.output
03:
	dictknife shape src/02*.json --skiplist > dst/$@.output
04:
	dictknife shape src/02*.json --skiplist > dst/$@.output
05:
	dictknife shape src/03*.json --skiplist > dst/$@.output
06:
	dictknife shape src/03*.json --skiplist > dst/$@.output
07:
	cat src/03*.json | dictknife shape -i json --skiplist > dst/$@.output
08:
	cat src/03*.json | dictknife shape -i json --skiplist src/0{0,1}*.json > dst/$@.output
