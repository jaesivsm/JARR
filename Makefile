GUNICORN_CONF = example_conf/gunicorn.py
LOG_CONFIG = example_conf/logging.ini
CONF_FILE ?= example_conf/jarr.json
SERVER_PORT = 8000
SERVER_ADDR = 0.0.0.0
DB_VER = $(shell pipenv run ./manager.py db heads | sed -e 's/ .*//g')
COMPOSE_FILE ?= Dockerfiles/dev-env.yml
RUN = PIPENV_IGNORE_VIRTUALENVS=1 pipenv run
COMPOSE = $(RUN) docker-compose --project-name jarr --file $(COMPOSE_FILE)
TEST = tests/
DB_NAME ?= jarr
PUBLIC_URL ?=
REACT_APP_API_URL ?=

install:
	pipenv sync --dev

pep8:
	$(RUN) pycodestyle --ignore=E126,E127,E128,W503 jarr/ --exclude=jarr/migrations

mypy:
	$(RUN) mypy jarr --ignore-missing-imports --exclude=jarr/crawler/lib/__init__.py

lint: pep8 mypy

test: export JARR_CONFIG = example_conf/jarr.test.json
test:
	$(RUN) nosetests $(TEST) -vv --with-coverage --cover-package=jarr

build-base:
	docker build --cache-from=jarr . \
		--file Dockerfiles/pythonbase \
		-t jarr-base

build-server: build-base
	docker build --cache-from=jarr . \
		--file Dockerfiles/server \
		-t jarr-server

build-worker: build-base
	docker build --cache-from=jarr . \
		--file Dockerfiles/worker \
		-t jarr-worker

build-front:
	docker build --cache-from=jarr . \
		--file Dockerfiles/front -t jarr-front \
		--build-arg PUBLIC_URL=$(PUBLIC_URL) \
		--build-arg REACT_APP_API_URL=$(REACT_APP_API_URL)

start-env:
	$(COMPOSE) up -d

run-server: export JARR_CONFIG = $(CONF_FILE)
run-server:
	$(RUN) gunicorn -c $(GUNICORN_CONF) -b $(SERVER_ADDR):$(SERVER_PORT) wsgi:application

run-worker: export JARR_CONFIG = $(CONF_FILE)
run-worker:
	$(RUN) celery worker --app ep_celery.celery_app

run-front:
	cd jsclient/; yarn start

create-db:
	$(COMPOSE) exec postgresql su postgres -c \
		"createuser $(DB_NAME) --no-superuser --createdb --no-createrole"
	$(COMPOSE) exec postgresql su postgres -c "createdb $(DB_NAME) --no-password"

init-env: export JARR_CONFIG = $(CONF_FILE)
init-env:
	$(RUN) ./manager.py db_create
	$(RUN) ./manager.py db stamp $(DB_VER)

stop-env:
	$(COMPOSE) down --remove-orphans

clean-env: stop-env
	$(COMPOSE) rm --force

status-env:
	$(COMPOSE) ps

setup-testing: export DB_NAME=jarr_test
setup-testing: export JARR_CONFIG=example_conf/jarr.test.json
setup-testing: export CONF_FILE=example_conf/jarr.test.json
setup-testing:
	make start-env
	sleep 2
	make create-db
	make init-env
