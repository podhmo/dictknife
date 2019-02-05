defaut: 00 01 02 03

00:
	mkdir -p dst
	dictknife cat 00person.json --dst dst/00person.json
	dictknife --compact cat 00person.json --dst dst/00person.compact.json
	dictknife cat 00person.json --dst dst/00person.yaml
	dictknife cat 00person.json --dst dst/00person.toml
	dictknife cat 00person.json --dst dst/00person.csv
01:
	dictknife --flatten cat 01nested.json --dst dst/01nested.flatten.json
	dictknife cat 01nested.json --dst dst/01nested.csv
	dictknife --flatten cat 01nested.json --dst dst/01nested.flatten.csv
02:
	dictknife --unescape unicode cat 02unescape_unicode.json --dst dst/02unescape_unicode.json
	dictknife --unescape url cat 02unescape_url.json --dst dst/02unescape_url.json
03:
	dictknife cat --extra--fullscan 03people.json --dst dst/03people.csv
	dictknife cat 03people.json -o csv &> dst/03people.ng.csv || echo ok
