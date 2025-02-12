COMPOSE=docker compose
DOCKER=$(COMPOSE) run --rm ocr

.PHONY: build

build:
	$(COMPOSE) build --no-rm --parallel

services:
	$(COMPOSE) up -d --remove-orphans postgres

shell: services
	$(DOCKER) /bin/bash
