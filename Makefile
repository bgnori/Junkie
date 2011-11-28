
.PHONY: env build clean

env:
	python bootstrap.py --distribute

build: buildout.cfg
	bin/buildout

buildout.cfg: freeze.txt buildout.in
	python makeconfig.py

freeze.txt:
	pip freeze > freeze.txt

clean:
	rm -f depot/*
