default: 00 01 02 03 04 05 06 07 08 09 10 11 12 13

output:
	mkdir -p output
00: output
	dictknife mkdict --name "foo bar" 2>&1 > output/00.json
01: output
	dictknife mkdict --name foo --age 20 2>&1 > output/01.json
02: output
	dictknife mkdict --name foo --age 20 --name bar 2>&1 > output/02.json
03: output
	dictknife mkdict --name foo --age 20 ";" --name bar 2>&1 > output/03.json
04: output
	dictknife mkdict --squash --name foo --age 20 ";" --name bar 2>&1 > output/04.json
05: output
	dictknife mkdict name foo age 20 father/name X mother/name Y 2>&1 > output/05.json
06: output
	dictknife mkdict --separator=. name foo age 20 father.name X mother.name Y 2>&1 > output/06.json
07: output
	dictknife mkdict --message='foo --age 20' 2>&1 > output/07.json
08: output
	cat 08input.txt | dictknife mkdict --squash 2>&1 > output/08.json
09: output
	dictknife mkdict @ob/name foo @ob/age 40 name bar age 20 parent "&ob" ";" name boo age 18 parent "&ob" 2>&1 > output/09.json
10: output
	dictknife mkdict @x val use "&x" dont-ref "&&x" @@dont-assign "v" 2>&1 > output/10.json
11: output
	dictknife mkdict /name foo /name bar /name boo > output/11.json
12: output
	dictknife mkdict x foo ";" y bar ";" x boo > output/12.json
13: output
	dictknife mkdict x foo y bar z boo ";" > output/13.json

