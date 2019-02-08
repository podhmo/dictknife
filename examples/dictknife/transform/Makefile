default: 00 01 02 03

00:
	dictknife transform --src person.json --fn flatten -o json &> 00.json
01:
	dictknife transform --src person.json --fn flatten --fn only_num -o json &> 01.json
02:
	dictknife transform --src person.json --fn flatten --fn rows -o csv &> 02.csv
03:
	dictknife transform --src person.json --fn flatten --fn rows -o md &> 03.md
