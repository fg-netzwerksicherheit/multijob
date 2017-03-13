NAME = multijob
SETUPPY := python setup.py
AUTODOC_DEFAULTS := members,show-inheritance
OPEN_BROWSER := xdg-open
DOCS_SRC = ./docs-src
DOCS_HTML_TARGET = ./docs


.PHONY: all
all: docs test

.PHONY: test
test:
	$(SETUPPY) test

.PHONY: docs
docs: $(DOCS_SRC)/api/$(NAME).rst
	$(SETUPPY) build_sphinx -b coverage
	$(SETUPPY) build_sphinx -b html
	@ rm -rf $(DOCS_HTML_TARGET)
	cp -rT ./build/sphinx/html $(DOCS_HTML_TARGET)
	@ cat ./build/sphinx/coverage/python.txt

$(DOCS_SRC)/api/%.rst:
	@ [ -d $(DOCS_SRC)/api ] || mkdir $(DOCS_SRC)/api
	SPHINX_APIDOC_OPTIONS='$(AUTODOC_DEFAULTS)' \
		sphinx-apidoc -o $(DOCS_SRC)/api $* \
			--force --separate \
			--module-first \
			--no-toc

.PHONY: clean
clean:
	@ rm -rf build/
	@ rm -rf $(DOCS_HTML_TARGET)
	@ rm -rf $(DOCS_SRC)/api
