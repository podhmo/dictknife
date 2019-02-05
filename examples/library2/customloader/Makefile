default: clean 00 01
dst:
	mkdir -p dst
00: dst
	python loader.py src/main.yaml > dst/loader.output
01: dst
	python loader2.py src/main.yaml > dst/loader2.output
clean:
	rm -rf dst
