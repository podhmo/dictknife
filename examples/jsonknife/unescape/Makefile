default: 00 01 02 03 04
00:
	jsonknife unescape 00escaped.json --dst output/00unescaped.json
01:
	jsonknife unescape 01escaped.json --dst output/01unescaped.json
02:
	jsonknife unescape 02escaped.json --dst output/02unescaped.json
03:
	cat 00escaped.json | jsonknife unescape -i json --dst output/03unescaped.json
04:
	jsonknife unescape 04multiline.json -i json --dst output/04multiline.json
	jsonknife unescape 04multiline.json -i json --dst output/04multiline.yaml
clean:
	rm -rf output
