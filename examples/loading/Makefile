default: 02 03

# dump single
00: 00person.json
	mkdir -p dst
	dictknife concat $< --dst dst/00output.json
	dictknife concat $< --dst dst/00output.yaml
	dictknife concat $< --dst dst/00output.toml
	dictknife concat $< --dst dst/00output.tsv

# dump multi
01: 01people.json
	mkdir -p dst
	dictknife concat $< --dst dst/01output.json
	dictknife concat $< --dst dst/01output.yaml
	# dictknife concat $< --dst dst/01output.toml
	dictknife concat $< --dst dst/01output.tsv

# load single
02: 00
	mkdir -p dst
	dictknife concat dst/00output.json --dst dst/02output.json.json
	dictknife concat dst/00output.yaml --dst dst/02output.yaml.json
	dictknife concat dst/00output.toml --dst dst/02output.toml.json
	dictknife concat dst/00output.tsv --dst dst/02output.tsv.json

# load multi
03: 01
	mkdir -p dst
	dictknife concat dst/01output.json --dst dst/03output.json.json
	dictknife concat dst/01output.yaml --dst dst/03output.yaml.json
	# dictknife concat dst/01output.toml --dst dst/03output.toml.json
	dictknife concat dst/01output.tsv --dst dst/03output.tsv.json
