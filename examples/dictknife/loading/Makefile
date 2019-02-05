default: 00 01 02 03 06 07

dst:
	mkdir -p dst

# dump single
00: src/00person.json dst
	dictknife cat $< --dst dst/00output.json
	dictknife cat $< --dst dst/00output.yaml
	dictknife cat $< --dst dst/00output.toml
	dictknife cat $< --dst dst/00output.tsv
	dictknife cat $< --dst dst/00output.csv
	dictknife cat $< --dst dst/00output.md

# dump multi
01: src/01people.json dst
	dictknife cat $< --dst dst/01output.json
	dictknife cat $< --dst dst/01output.yaml
	# dictknife cat $< --dst dst/01output.toml
	dictknife cat $< --dst dst/01output.tsv
	dictknife cat $< --dst dst/01output.csv
	dictknife cat $< --dst dst/01output.md

# load single
02: src/00 dst
	dictknife cat dst/00output.json --dst dst/02output.json.json
	dictknife cat dst/00output.yaml --dst dst/02output.yaml.json
	dictknife cat dst/00output.toml --dst dst/02output.toml.json
	dictknife cat dst/00output.tsv --dst dst/02output.tsv.json
	dictknife cat dst/00output.csv --dst dst/02output.csv.json
	dictknife cat dst/00output.md --dst dst/02output.md.json

# load multi
03: src/01 dst
	dictknife cat dst/01output.json --dst dst/03output.json.json
	dictknife cat dst/01output.yaml --dst dst/03output.yaml.json
	# dictknife cat dst/01output.toml --dst dst/03output.toml.json
	dictknife cat dst/01output.tsv --dst dst/03output.tsv.json
	dictknife cat dst/01output.csv --dst dst/03output.csv.json
	dictknife cat dst/01output.md --dst dst/03output.md.json

# load with ignore error
04: src/02encoding-error.csv
	dictknife cat $< --errors=replace
	dictknife cat $< --errors=ignore
	dictknife cat $<
05: src/02quote-error.csv
	dictknife cat $< --errors=ignore

06: src/06missing.json dst
	dictknife cat $< --dst dst/06output.json
	dictknife cat $< --dst dst/06output.yaml
	# dictknife cat $< --dst dst/06output.toml
	# dictknife cat $< --dst dst/06output.tsv
	# dictknife cat $< --dst dst/06output.csv
	dictknife cat $< --dst dst/06output.md

# size
07: src/07alphabets.csv dst
	dictknife cat $< --size=5 --dst dst/07output.json
	dictknife cat $< --size=5 --dst dst/07output.yaml
	dictknife cat $< --size=5 --dst dst/07output.tsv
	dictknife cat $< --size=5 --dst dst/07output.md
