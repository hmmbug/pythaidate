.PHONY: test sbuild wbuild clean

# Random sampling of test data in some tests
RUN_PERCENT ?= 5

test:
	RUN_PERCENT=$(RUN_PERCENT) python3 -m unittest discover -v

test-coverage:
	@date
	RUN_PERCENT=$(RUN_PERCENT) coverage run -m unittest discover
	coverage html
	coverage report
	@date

build: clean-build
	python3 -m build --sdist
	python3 -m build --wheel

upload-prod:
	twine upload --repository testpypi dist/*
	mkdir -p releases-prod
	cp dist/* releases-prod/

upload-test:
	twine upload --repository testpypi dist/*
	mkdir -p releases-test
	cp dist/* releases-test/

clean: clean-build
	py3clean .

clean-build:
	rm -rf build dist pythaidate.egg-info pythaidate/pythaidate.egg-info

clean-all: clean
	rm -rf htmlcov .coverage
