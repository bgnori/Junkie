
.PHONY: env build clean test lint


PY = \
	cache.py\
	proxy.py\
	dnmapper.py\
	tumblr/__init__.py\
	tumblr/junkie.py\
	tumblr/model.py\
	tumblr/render.py\
	test/*.py

TESTPY = test/*.py

# todo:
#   Add script to measure McCabe Chromatic Complexity
#   note: known http://www.journyx.com/curt/complexity.html is GONE!
#

test:  nose lint
	echo 'done'

nose:
	nosetests --with-coverage --with-doctest --with-isolation -w test

lint: 
	pylint --include-ids=y --files-output=y --comment=y -f parseable -d W0311 $(PY)
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


