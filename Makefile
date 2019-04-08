# http://clarkgrubb.com/makefile-style-guide

BIN := venv/bin
ISORT := $(BIN)/isort
PIP := $(BIN)/pip
PIP-COMPILE := $(BIN)/pip-compile
PYTEST := $(BIN)/pytest
PYTHON := $(BIN)/python
TWINE := $(BIN)/twine
FLAKE8 := $(BIN)/flake8

.PHONY: venv
venv:
	@rm -rf $@
	@virtualenv -p python3.7 $@
	@$(PIP) install -r requirements.txt
	@$(PIP) install pip-tools isort pytest flake8
	@$(PIP) install -e .

.PHONY: requirements.txt
requirements.txt:
	@$(PIP-COMPILE) --no-index --no-emit-trusted-host --generate-hashes --output-file $@ setup.py

.PHONY: test
test:
	@$(PYTEST)
	@$(FLAKE8) bestmobabot tests
	@$(ISORT) -rc -c bestmobabot tests

.PHONY: tag
tag:
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git tag -a '$(VERSION)' -m '$(VERSION)'

.PHONY: publish/tag
publish/tag:
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@git push origin '$(VERSION)'

.PHONY: docker
docker:
	@docker build -t eigenein/bestmobabot .

.PHONY: publish
publish: docker
	@$(eval VERSION = $(shell $(PYTHON) setup.py --version))
	@docker tag 'eigenein/bestmobabot:latest' 'eigenein/bestmobabot:$(VERSION)'
	@docker push 'eigenein/bestmobabot:latest'
	@docker push 'eigenein/bestmobabot:$(VERSION)'

.PHONY: publish/latest
publish/latest: docker
	@docker push 'eigenein/bestmobabot:latest'

.PHONY: deploy/latest
deploy/latest: publish/latest
	ssh moon.eigenein.com 'docker pull eigenein/bestmobabot && docker-compose up -d --remove-orphans'

.PHONY: resources
resources:
	curl 'https://heroes.cdnvideo.ru/vk/v0498/locale/ru.json.gz?js=1' --output bestmobabot/js/ru.json.gz
	curl 'https://heroes.cdnvideo.ru/vk/v0497/lib/lib.json.gz?js=1' --output bestmobabot/js/lib.json.gz
	curl 'https://heroes.cdnvideo.ru/vk/v0497/assets/heroes.js' --output bestmobabot/js/heroes.js
	curl 'https://heroes.cdnvideo.ru/vk/v0497/assets/hx/skills.sc?js=1' --output bestmobabot/js/skills.sc

docs: book
	mdbook build
