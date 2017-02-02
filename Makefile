NAME = multiprocessor
SETUPPY := python setup.py
AUTODOC_DEFAULTS := members,show-inheritance
OPEN_BROWSER := xdg-open

.PHONY: all
all: docs test

.PHONY: test
test:
	$(SETUPPY) test

.PHONY: docs
docs: docs/api/$(NAME).rst
	$(SETUPPY) build_sphinx -b coverage
	$(SETUPPY) build_sphinx -b html
	@ cat ./build/sphinx/coverage/python.txt

docs/api/%.rst:
	@ [ -d docs/api ] || mkdir docs/api
	SPHINX_APIDOC_OPTIONS='$(AUTODOC_DEFAULTS)' \
		sphinx-apidoc -o docs/api $* \
			--force --separate \
			--module-first \
			--no-toc

.PHONY: clean
clean:
	@ rm -rf build/
	@ rm -rf docs/api
