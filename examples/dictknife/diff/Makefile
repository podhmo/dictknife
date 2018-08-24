default: 00 01

# basic
00:
	dictknife diff 000person.json 001person.json > 00.diff
	dictknife diff 000person.json 001person.json --sort-keys > 00.sorted.diff
	dictknife diff 000person.json 001person.json -o md > 00.md
# list
01:
	dictknife diff 010people.tsv 011people.tsv > 01.diff
	dictknife diff 010people.tsv 011people.tsv --sort-keys > 01.sorted.diff
	dictknife diff 010people.tsv 011people.tsv -o md > 01.md
	dictknife diff 010people.tsv 011people.tsv --skip-empty -o md > 01.skipped.md
