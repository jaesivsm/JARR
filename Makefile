GUNICORN_CONF = example_conf/gunicorn.py
LOG_CONFIG = example_conf/logging.ini
CONF_FILE ?= example_conf/jarr.json
SERVER_PORT = 8000
SERVER_ADDR = 0.0.0.0
DB_VER = $(shell pipenv run flask db heads | tail -n1 | sed -e 's/ .*//g')
COMPOSE_FILE ?= Dockerfiles/dev-env.yml
RUN = FLASK_APP=wsgi PIPENV_IGNORE_VIRTUALENVS=1 pipenv run
COMPOSE = $(RUN) docker compose --project-name jarr --file $(COMPOSE_FILE)
TEST = tests/
DB_NAME ?= jarr
PUBLIC_URL ?=
REACT_APP_API_URL ?=
QUEUE ?= jarr,jarr-crawling,jarr-clustering
DB_CONTAINER_NAME = postgres
QU_CONTAINER_NAME = rabbitmq

install:
	pipenv sync --dev

pep8:
	$(RUN) pycodestyle --ignore=E126,E127,E128,W503 jarr/ --exclude=jarr/migrations

mypy:
	$(RUN) mypy jarr --ignore-missing-imports --exclude=jarr/crawler/lib/__init__.py

lint: pep8 mypy

test: export JARR_CONFIG = example_conf/jarr.test.json
test:
	$(RUN) pytest --cov=jarr $(TEST) -vv

DOCKER_USER ?=
CACHE_TAG ?= latest
DOCKER_TAG ?= latest

build-base:
	docker pull $(DOCKER_USER)/jarr-base:$(CACHE_TAG) || \
		docker pull $(DOCKER_USER)/jarr-base:develop || \
		docker pull $(DOCKER_USER)/jarr-base:latest || true
	docker build \
		--cache-from=$(DOCKER_USER)/jarr-base:$(CACHE_TAG) \
		--cache-from=$(DOCKER_USER)/jarr-base:develop \
		--cache-from=$(DOCKER_USER)/jarr-base:latest . \
		--file Dockerfiles/pythonbase \
		-t jarr-base \
		-t $(DOCKER_USER)/jarr-base:$(DOCKER_TAG)

build-server:
	docker pull $(DOCKER_USER)/jarr-server:$(CACHE_TAG) || \
		docker pull $(DOCKER_USER)/jarr-server:develop || \
		docker pull $(DOCKER_USER)/jarr-server:latest || true
	docker build \
		--cache-from=$(DOCKER_USER)/jarr-server:$(CACHE_TAG) \
		--cache-from=$(DOCKER_USER)/jarr-server:develop \
		--cache-from=$(DOCKER_USER)/jarr-server:latest \
		--cache-from=jarr-base . \
		--file Dockerfiles/server \
		-t jarr-server \
		-t $(DOCKER_USER)/jarr-server:$(DOCKER_TAG)

build-worker:
	docker pull $(DOCKER_USER)/jarr-worker:$(CACHE_TAG) || \
		docker pull $(DOCKER_USER)/jarr-worker:develop || \
		docker pull $(DOCKER_USER)/jarr-worker:latest || true
	docker build \
		--cache-from=$(DOCKER_USER)/jarr-worker:$(CACHE_TAG) \
		--cache-from=$(DOCKER_USER)/jarr-worker:develop \
		--cache-from=$(DOCKER_USER)/jarr-worker:latest \
		--cache-from=jarr-base . \
		--file Dockerfiles/worker \
		-t jarr-worker \
		-t $(DOCKER_USER)/jarr-worker:$(DOCKER_TAG)

build-front:
	docker pull $(DOCKER_USER)/jarr-front:$(CACHE_TAG) || \
		docker pull $(DOCKER_USER)/jarr-front:develop || \
		docker pull $(DOCKER_USER)/jarr-front:latest || true
	docker build \
		--cache-from=$(DOCKER_USER)/jarr-front:$(CACHE_TAG) \
		--cache-from=$(DOCKER_USER)/jarr-front:develop \
		--cache-from=$(DOCKER_USER)/jarr-front:latest . \
		--file Dockerfiles/front -t jarr-front \
		-t $(DOCKER_USER)/jarr-front:$(DOCKER_TAG) \
		--build-arg PUBLIC_URL=$(PUBLIC_URL) \
		--build-arg REACT_APP_API_URL=$(REACT_APP_API_URL)

start-env:
	$(COMPOSE) up -d

run-server: export JARR_CONFIG = $(CONF_FILE)
run-server:
	$(RUN) gunicorn -c $(GUNICORN_CONF) -b $(SERVER_ADDR):$(SERVER_PORT) wsgi:application

run-worker: export JARR_CONFIG = $(CONF_FILE)
run-worker:
	$(RUN) celery --app ep_celery.celery_app worker -Q $(QUEUE) --hostname "$(QUEUE)@%h"

run-front:
	cd jsclient/; yarn start

db-bootstrap-user:
	$(COMPOSE) exec $(DB_CONTAINER_NAME) su postgres -c \
		"createuser $(DB_NAME) --superuser --createdb"

db-bootstrap-tables:
	$(COMPOSE) exec $(DB_CONTAINER_NAME) su postgres -c "createdb $(DB_NAME) --no-password"
	$(COMPOSE) exec $(DB_CONTAINER_NAME) psql -h 0.0.0.0 -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $(DB_NAME) to $(DB_NAME);"

db-import-dump:
	docker cp $(DUMP) jarr_$(DB_CONTAINER_NAME)_1:/tmp/dump.pgsql
	$(COMPOSE) exec $(DB_CONTAINER_NAME) su postgres -c "pg_restore -d $(DB_NAME) /tmp/dump.pgsql"
	$(COMPOSE) exec $(DB_CONTAINER_NAME) rm /tmp/dump.pgsql

init-env: export JARR_CONFIG = $(CONF_FILE)
init-env:
	$(RUN) flask bootstrap-database
	$(RUN) flask db stamp $(DB_VER)

init-env-docker: export JARR_CONFIG = $(CONF_FILE)
init-env-docker:
	$(COMPOSE) exec jarr-server pipenv run flask bootstrap-database
	$(COMPOSE) exec jarr-server pipenv run flask db stamp $(DB_VER)

db: export JARR_CONFIG = $(CONF_FILE)
db:
	$(RUN) flask db $(COMMAND)

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
	@echo "### waiting for database to be available"
	sleep 2
	make db-bootstrap-user
	make db-bootstrap-tables
	make init-env

init-rabbitmq:
	$(COMPOSE) exec $(QU_CONTAINER_NAME) rabbitmqctl add_user jarr jarr
	$(COMPOSE) exec $(QU_CONTAINER_NAME) rabbitmqctl add_vhost jarr
	$(COMPOSE) exec $(QU_CONTAINER_NAME) rabbitmqctl set_user_tags jarr
	$(COMPOSE) exec $(QU_CONTAINER_NAME) rabbitmqctl set_permissions -p jarr jarr ".*" ".*" ".*"

init-worker:
	$(RUN) python -c "from jarr.crawler.main import scheduler;scheduler()"
