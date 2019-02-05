default: clean 00
dst:
	mkdir -p dst
00: dst
	python loader.py src/main.yaml > dst/loader.output
clean:
	rm -rf dst
