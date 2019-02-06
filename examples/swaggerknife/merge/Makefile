default: 00 01

dst:
	mkdir -p dst

00: dst
	swaggerknife merge src/*.json --dst dst/00ref.json
01: dst
	swaggerknife merge src/*.json --style=whole --dst dst/01whole.json

# strict
