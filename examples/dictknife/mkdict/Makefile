default: 00 01 02 03 04 05 06 07 08
00:
	mkdir -p output
	dictknife mkdict --name "foo bar" | tee output/00.json
01:
	mkdir -p output
	dictknife mkdict --name foo --age 20 | tee output/01.json
02:
	mkdir -p output
	dictknife mkdict --name foo --age 20 --name bar | tee output/02.json
03:
	mkdir -p output
	dictknife mkdict --name foo --age 20 ";" --name bar | tee output/03.json
04:
	mkdir -p output
	dictknife mkdict --squash --name foo --age 20 ";" --name bar | tee output/04.json
05:
	mkdir -p output
	dictknife mkdict name foo age 20 father/name X mother/name Y | tee output/05.json
06:
	mkdir -p output
	dictknife mkdict --separator=. name foo age 20 father.name X mother.name Y | tee output/06.json
07:
	mkdir -p output
	dictknife mkdict --message='foo --age 20' | tee output/07.json
08:
	mkdir -p output
	cat 08input.txt | dictknife mkdict --squash | tee output/08.json
