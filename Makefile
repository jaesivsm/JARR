GUNICORN_CONF = example_conf/gunicorn.py
LOG_CONFIG = example_conf/logging.ini
CONF_FILE = example_conf/jarr.json
SERVER_PORT = 8000
SERVER_ADDR = 0.0.0.0
DB_VER = $(shell pipenv run ./manager.py db heads | sed -e 's/ .*//g')
ENV = dev
COMPOSE = pipenv run docker-compose --project-name jarr --file Dockerfiles/$(ENV)-env.yml
TEST = tests/
DB_NAME = jarr_test

install:
	pipenv sync --dev

pep8:
	pipenv run pycodestyle --ignore=E126,E127,E128,W503 jarr/ --exclude=jarr/migrations

mypy:
	pipenv run mypy jarr --ignore-missing-imports

lint: pep8 mypy

test: export JARR_CONFIG = example_conf/jarr.test.json
test:
	pipenv run nosetests $(TEST) -vv --with-coverage --cover-package=jarr

build-base:
	docker build --cache-from=jarr . --file Dockerfiles/pythonbase -t jarr-base

build-server: build-base
	docker build --cache-from=jarr . --file Dockerfiles/server -t jarr-server

build-worker: build-base
	docker build --cache-from=jarr . --file Dockerfiles/worker -t jarr-worker

start-env:
	$(COMPOSE) up -d

run-server: export JARR_CONFIG = $(CONF_FILE)
run-server:
	pipenv run gunicorn -c $(GUNICORN_CONF) -b $(SERVER_ADDR):$(SERVER_PORT) wsgi:application

run-worker: export JARR_CONFIG = $(CONF_FILE)
run-worker:
	pipenv run celery worker --app ep_celery.celery_app

create-db:
	$(COMPOSE) exec postgresql su postgres -c \
		"createuser $(DB_NAME) --no-superuser --createdb --no-createrole"
	$(COMPOSE) exec postgresql su postgres -c "createdb $(DB_NAME) --no-password"

init-env: export JARR_CONFIG = $(CONF_FILE)
init-env:
	pipenv run ./manager.py db_create
	pipenv run ./manager.py db stamp $(DB_VER)

stop-env:
	$(COMPOSE) down --remove-orphans

clean-env: stop-env
	$(COMPOSE) rm --force

status-env:
	$(COMPOSE) ps
