default: 00 01 02 03 04 05 06 07 08 09 10
00:
	mkdir -p output
	dictknife mkdict --name "foo bar" &> output/00.json
01:
	mkdir -p output
	dictknife mkdict --name foo --age 20 &> output/01.json
02:
	mkdir -p output
	dictknife mkdict --name foo --age 20 --name bar &> output/02.json
03:
	mkdir -p output
	dictknife mkdict --name foo --age 20 ";" --name bar &> output/03.json
04:
	mkdir -p output
	dictknife mkdict --squash --name foo --age 20 ";" --name bar &> output/04.json
05:
	mkdir -p output
	dictknife mkdict name foo age 20 father/name X mother/name Y &> output/05.json
06:
	mkdir -p output
	dictknife mkdict --separator=. name foo age 20 father.name X mother.name Y &> output/06.json
07:
	mkdir -p output
	dictknife mkdict --message='foo --age 20' &> output/07.json
08:
	mkdir -p output
	cat 08input.txt | dictknife mkdict --squash &> output/08.json
09:
	mkdir -p output
	dictknife mkdict @ob/name foo @ob/age 40 name bar age 20 parent "&ob" ";" name boo age 18 parent "&ob" &> output/09.json
10:
	mkdir -p output
	dictknife mkdict @x val use "&x" dont-ref "&&x" @@dont-assign "v" &> output/10.json
