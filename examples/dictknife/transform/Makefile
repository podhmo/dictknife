default: 00 01 02 03

00:
	dictknife transform --src person.json --fn flatten -o json 2>&1 > 00.json
01:
	dictknife transform --src person.json --fn flatten --fn only_num -o json 2>&1 > 01.json
02:
	dictknife transform --src person.json --fn flatten --fn rows -o csv 2>&1 > 02.csv
03:
	dictknife transform --src person.json --fn flatten --fn rows -o md 2>&1 > 03.md
