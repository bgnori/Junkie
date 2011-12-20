
.PHONY: env build clean test lint


SRCDIR = src/
SRC = \
	cache.py\
	app.py\
	proxy.py\
	dnmapper.py\
	tumblr/__init__.py\
	tumblr/junkie.py\
	tumblr/model.py\
	tumblr/render.py

TESTDIR = test/*.py
TEST = test/*.py


PY = $(SRC) $(TEST)

# todo:
#   Add script to measure McCabe Chromatic Complexity
#   note: known http://www.journyx.com/curt/complexity.html is GONE!
#

test:  nose lint
	echo 'done'

nose:
	nosetests test
#nosetests --with-coverage --with-doctest --with-isolation test

lint: 
	pylint --include-ids=y --files-output=y --comment=y -f parseable -d W0311 src/*
#no warning for 2-space indentation


env: 
	pip install -r freeze.txt

develop:
	python setup.py develop

freeze.txt:
	pip freeze > freeze.txt

clean:
	python setup.py clean
	rm -f build/*


