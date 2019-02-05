default: 00 01

dst:
	mkdir -p dst
# basic
00: dst
	dictknife diff src/000person.json src/001person.json > dst/00.diff
	dictknife diff src/000person.json src/001person.json --sort-keys > dst/00.sorted.diff
	dictknife diff src/000person.json src/001person.json -o md > dst/00.md
	dictknife diff src/000person.json src/001person.json -o dict > dst/00.dict
	dictknife diff src/000person.json src/001person.json -o tsv > dst/00.tsv
	dictknife diff src/000person.json src/001person.json -o jsonpatch > dst/00.jsonpatch
	dictknife diff --verbose src/000person.json src/001person.json -o jsonpatch > dst/00.jsonpatch2

# list
01: dst
	dictknife diff src/010people.tsv src/011people.tsv > dst/01.diff
	dictknife diff src/010people.tsv src/011people.tsv --sort-keys > dst/01.sorted.diff
	dictknife diff src/010people.tsv src/011people.tsv -o md > dst/01.md
	dictknife diff src/010people.tsv src/011people.tsv --skip-empty -o md > dst/01.skipped.md
	dictknife diff src/010people.tsv src/011people.tsv --verbose -o jsonpatch > dst/01.jsonpatch
