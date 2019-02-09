default: 00 01 02 03

dst:
	mkdir -p dst

00: dst
	swaggerknife merge src/*.json --dst dst/00ref.json
01: dst
	swaggerknife merge src/*.json --style=whole --dst dst/01whole.json

# conflicted
02: dst
	(swaggerknife merge src/*.json src/conflicted/*.json --strict --dst dst/02ref.json 2>&1 > dst/02conflicted.error) || exit 0

# --wrap
03: dst
	swaggerknife merge src/*.json --wrap config --wrap-section=definitions --dst dst/03with-wrap.json
