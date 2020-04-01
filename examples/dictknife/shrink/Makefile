SHELL := $(shell which bash)
# TEE ?= 2>&1 | tee
TEE ?= 2>&1 > 

00:
	dictknife shrink $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json
	dictknife diff $(shell echo $@*/){data.json,data.output.json} $(TEE) $(shell echo $@*/)a.diff

# --with-tail
01:
	dictknife shrink --with-tail $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json
	dictknife diff $(shell echo $@*/){data.json,data.output.json} $(TEE) $(shell echo $@*/)a.diff

# stdin
02:
	cat $(shell echo $@*/)data.json | dictknife shrink -i json $(TEE) $(shell echo $@*/)data.output.json
