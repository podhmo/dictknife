SHELL := $(shell which bash)
# TEE ?= 2>&1 | tee
TEE ?= 2>&1 > 

00:
	dictknife shrink $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json

# --with-tail
01:
	dictknife shrink --with-tail $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json

# stdin
02:
	cat $(shell echo $@*/)data.json | dictknife shrink -i json $(TEE) $(shell echo $@*/)data.output.json

# --max-length-of-string --max-length-of-list
03:
	dictknife shrink --max-length-of-string=16 --max-length-of-list=1 $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json
