defaut: 00 01 02 03
OPTS ?= 
00:
	mkdir -p dst
	dictknife ${OPTS} cat 00person.json --dst dst/00person.json
	dictknife ${OPTS} --compact cat 00person.json --dst dst/00person.compact.json
	dictknife ${OPTS} cat 00person.json --dst dst/00person.yaml
	dictknife ${OPTS} cat 00person.json --dst dst/00person.toml
	dictknife ${OPTS} cat 00person.json --dst dst/00person.csv
01:
	dictknife ${OPTS} --flatten cat 01nested.json --dst dst/01nested.flatten.json
	dictknife ${OPTS} cat 01nested.json --dst dst/01nested.csv
	dictknife ${OPTS} --flatten cat 01nested.json --dst dst/01nested.flatten.csv
02:
	dictknife ${OPTS} --unescape unicode cat 02unescape_unicode.json --dst dst/02unescape_unicode.json
	dictknife ${OPTS} --unescape url cat 02unescape_url.json --dst dst/02unescape_url.json
03:
	dictknife ${OPTS} cat --extra--fullscan 03people.json --dst dst/03people.csv
	dictknife ${OPTS} cat 03people.json -o csv 2>&1 > dst/03people.ng.csv || echo ok
