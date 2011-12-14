
.PHONY: env build clean test

test:
	nosetests --with-coverage --with-doctest --with-isolation test

env:
	pip install -r freeze.txt

freeze.txt:
	pip freeze > freeze.txt

clean:
	rm -f depot/*
