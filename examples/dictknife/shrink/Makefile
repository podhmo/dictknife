SHELL := $(shell which bash)
# TEE ?= 2>&1 | tee
TEE ?= 2>&1 > 

00:
	dictknife shrink $(shell echo $@*/)data.json $(TEE) $(shell echo $@*/)data.output.json
	dictknife diff $(shell echo $@*/){data.json,data.output.json} $(TEE) $(shell echo $@*/)a.diff
