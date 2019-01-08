PIP := venv/bin/pip
PIP-COMPILE := venv/bin/pip-compile
PYTEST := venv/bin/pytest
PYTHON := venv/bin/python
TWINE := venv/bin/twine
FLAKE8 := venv/bin/flake8

.PHONY : \
	requirements.txt \
	test \
	tag \
	publish/tag \
	docker \
	publish/docker \
	dist \
	publish/dist

venv :
	@rm -rf venv
	@virtualenv -p python3.7 venv
	@$(PIP) install -r requirements.txt
	@$(PIP) install pip-tools isort pytest flake8
	@$(PIP) install -e .

requirements.txt : setup.py
	@$(PIP-COMPILE) --no-index --no-emit-trusted-host --generate-hashes --output-file requirements.txt setup.py

make test :
	@$(FLAKE8) bestmobabot tests
	@$(PYTEST)

tag :
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git tag -a '$(VERSION)' -m '$(VERSION)'

publish/tag : tag
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git push origin '$(VERSION)'

docker :
	@docker build -t eigenein/bestmobabot .

publish/docker : docker
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@docker tag 'eigenein/bestmobabot:latest' 'eigenein/bestmobabot:$(VERSION)'
	@docker push 'eigenein/bestmobabot:latest'
	@docker push 'eigenein/bestmobabot:$(VERSION)'

dist :
	@rm -rf dist
	@$(PYTHON) setup.py sdist bdist_wheel

publish/dist : dist
	@$(TWINE) upload --verbose dist/*
