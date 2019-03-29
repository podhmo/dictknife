default: 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14

dst:
	mkdir -p dst
00: dst
	dictknife mkdict --name "foo bar" 2>&1 > dst/00.json
01: dst
	dictknife mkdict --name foo --age 20 2>&1 > dst/01.json
02: dst
	dictknife mkdict --name foo --age 20 --name bar 2>&1 > dst/02.json
03: dst
	dictknife mkdict --name foo --age 20 ";" --name bar 2>&1 > dst/03.json
04: dst
	dictknife mkdict --squash --name foo --age 20 ";" --name bar 2>&1 > dst/04.json
05: dst
	dictknife mkdict name foo age 20 father/name X mother/name Y 2>&1 > dst/05.json
06: dst
	dictknife mkdict --separator=. name foo age 20 father.name X mother.name Y 2>&1 > dst/06.json
07: dst
	dictknife mkdict --message='foo --age 20' 2>&1 > dst/07.json
08: dst
	cat 08src/input.txt | dictknife mkdict --squash 2>&1 > dst/08.json
09: dst
	dictknife mkdict @ob/name foo @ob/age 40 name bar age 20 parent "&ob" ";" name boo age 18 parent "&ob" 2>&1 > dst/09.json
10: dst
	dictknife mkdict @x val use "&x" dont-ref "&&x" @@dont-assign "v" 2>&1 > dst/10.json
11: dst
	dictknife mkdict /name foo /name bar /name boo > dst/11.json
12: dst
	dictknife mkdict x foo ";" y bar ";" x boo > dst/12.json
13: dst
	dictknife mkdict x foo y bar z boo ";" > dst/13.json
14: dst
	dictknife mkdict @ob.name foo @ob.age 20 id 1 "" "&ob" ";" id 2 "&ob" > dst/14.json

