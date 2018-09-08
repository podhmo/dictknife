default: 00 01 02 03 04
00:
	mkdir -p output
	dictknife mkdict --name foo | tee output/00.json
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
