.PHONY: clean_pyc clean_coverage docs docs_install docs_rm init init-dev test

MODULE = pythaidate

SRC_FILES = $(shell find $(MODULE) -name '*.py' | sed '/__init__.py/d' | sort -u)

PKG_DOCS = $(shell find $(MODULE) -name '__init__.py' | sed 's=/__init__.py==; s=/=.=g; s=\(.*\)=\1.html=;' | sort -u)
MOD_DOCS = $(subst /,.,$(patsubst %.py, %.html, $(SRC_FILES)))
ALL_DOCS = $(MOD_DOCS) $(PKG_DOCS)

init:
	pip3 install -r requirements.txt

init-dev: init
	pip3 install -r requirements-dev.txt

test:
	nosetests --with-coverage --cover-erase --cover-package=pythaidate \
						--cover-html-dir=htmlcov --cover-html -v tests

# #### HOUSEKEEPING

clean: clean_pyc clean_coverage docs_rm

clean_coverage:
	rm -rf htmlcov

clean_pyc:
	find $(MODULE) tests -name '*.pyc' -delete

# ### DOCUMENTATION

docs: clean_pyc docs_rm $(ALL_DOCS) docs_install

# build docs for all source files, substituting / for . and remove .html to
# produce python module paths instead of file system paths
#
# pydoc is not installed in virtualenv so need to use "python -m pydoc ..." to
# avoid the system pydoc (https://github.com/pypa/virtualenv/issues/149)
$(ALL_DOCS): $(SRC_FILES)
	python -m pydoc -w $(subst /,.,$(subst .html,,$@))

# move all docs to the docs/ folder
docs_install:
	mv -f *.html docs/

# delete docs
docs_rm:
	rm -rf docs/*.html
