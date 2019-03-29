default: 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23

TEE := 2>&1 >

dst:
	mkdir -p dst

# handling arguments
00: dst
	dictknife mkdict --name "foo bar" ${TEE} dst/$@.json
01: dst
	dictknife mkdict --name foo --age 20 ${TEE} dst/$@.json
02: dst
	dictknife mkdict --name foo --age 20 --name bar ${TEE} dst/$@.json

# array with delimiter(;)
03: dst
	dictknife mkdict --name foo --age 20 ok true ng False ";" --name bar ${TEE} dst/$@.json
04: dst
	dictknife mkdict --squash --name foo --age 20 ";" --name bar ${TEE} dst/$@.json

# nested
05: dst
	dictknife mkdict name foo age 20 father/name X mother/name Y ${TEE} dst/$@.json
06: dst
	dictknife mkdict --separator=. name foo age 20 father.name X mother.name Y ${TEE} dst/$@.json

# quoted
07: dst
	dictknife mkdict --message='foo --age 20' ${TEE} dst/$@.json

# pipe
08: dst
	cat src/08input.txt | dictknife mkdict --squash ${TEE} dst/$@.json

# variables
09: dst
	dictknife mkdict @ob/name foo @ob/age 40 name bar age 20 parent "&ob" ";" name boo age 18 parent "&ob" ${TEE} dst/$@.json
10: dst
	dictknife mkdict @x val use "&x" dont-ref "&&x" @@dont-assign "v" ${TEE} dst/$@.json


# "" and / is not equal
11: dst
	dictknife mkdict /name foo /name bar /name boo ${TEE} dst/$@.json
	dictknife mkdict name foo name bar name boo ${TEE} dst/$@-2.json

# array or dict
12: dst
	dictknife mkdict x foo ";" y bar ";" x boo ${TEE} dst/$@.json
13: dst
	dictknife mkdict x foo y bar z boo ";" ${TEE} dst/$@.json
14: dst
	dictknife mkdict @ob.name foo @ob.age 20 id 1 "" "&ob" ";" id 2 "&ob" ${TEE} dst/$@.json

# block
15: dst
	dictknife mkdict ob { name foo age 20 } ${TEE} dst/$@.json
	dictknife mkdict id 1 ob { name foo age 20 } ${TEE} dst/$@-2.json
	dictknife mkdict ob { name foo age 20 } id 1 ${TEE} dst/$@-3.json
16: dst
	dictknife mkdict ob { father { name foo age 20 } } ${TEE} dst/$@.json
17: dst
	dictknife mkdict ob { items { "" 1 ";" "" 2 } } ${TEE} dst/$@.json
18: dst
	dictknife mkdict ob { items { "" 1 ";" } } ${TEE} dst/$@.json
19: dst
	dictknife mkdict ob { item { "" 1 } } ${TEE} dst/$@.json
20: dst  # ng
	dictknife mkdict ob { x { y z }} a b ${TEE} dst/$@.json

# block with variables
21: dst
	dictknife mkdict @father { name A age 20 } @mother { name B age 20 } name X age 0 father "&father" mother "&mother" ";" name Y age 1 father "&father" mother "&mother" ${TEE} dst/$@.json
22: dst
	dictknife mkdict @father { name A age 20 } @mother { name B age 20 } { name X age 0 father "&father" mother "&mother" } ";" { name Y age 1 father "&father" mother "&mother" } ${TEE} dst/$@.json

23: dst
	dictknife mkdict @v 10 x0 "&v" x1 { v "&v" } x2 { @v 20 v "&v" } x3 { v "&v" } x4 { v "&v" @v 100 y { v "&v" } } @v 11 x5 "&v" ${TEE} dst/$@.json
