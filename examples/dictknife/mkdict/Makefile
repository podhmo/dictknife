default: 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23

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
	cat src/08input.txt | dictknife mkdict --squash 2>&1 > dst/08.json
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

# block
15: dst
	dictknife mkdict ob { name foo age 20 } > dst/15.json
16: dst
	dictknife mkdict ob { father { name foo age 20 } } > dst/16.json
17: dst
	dictknife mkdict ob { items { "" 1 ";" "" 2 } } > dst/17.json
18: dst
	dictknife mkdict ob { items { "" 1 ";" } } > dst/18.json
19: dst
	dictknife mkdict ob { item { "" 1 } } > dst/19.json
20: dst  # ng
	dictknife mkdict ob { x { y z }} a b > dst/20.json

# block with variables
21: dst
	dictknife mkdict @father { name A age 20 } @mother { name B age 20 } name X age 0 father "&father" mother "&mother" ";" name Y age 1 father "&father" mother "&mother" > dst/21.json
22: dst
	dictknife mkdict @father { name A age 20 } @mother { name B age 20 } { name X age 0 father "&father" mother "&mother" } ";" { name Y age 1 father "&father" mother "&mother" } > dst/22.json

23: dst
	dictknife mkdict @v 10 x0 "&v" x1 { v "&v" } x2 { @v 20 v "&v" } x3 { v "&v" } x4 { v "&v" @v 100 y { v "&v" } } @v 11 x5 "&v" > dst/23.json
