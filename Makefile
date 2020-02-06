GUNICORN_CONF = example_conf/gunicorn.py
LOG_CONFIG = example_conf/logging.ini
CONF_FILE = example_conf/jarr.json
SERVER_PORT = 8000
SERVER_ADDR = 0.0.0.0
DB_VER = $(shell pipenv run ./manager.py db heads | sed -e 's/ .*//g')

install:
	pipenv sync --dev

pep8:
	pipenv run pycodestyle --ignore=E126,E127,E128,W503 jarr/ --exclude=jarr/migrations

pylint:
	pipenv run pylint -d I0011,R0901,R0902,R0801,C0111,C0103,C0411,C0415,C0330,R0903,R0913,R0914,R0915,R1710,W0613,W0703 jarr

mypy:
	pipenv run mypy jarr --ignore-missing-imports

lint: pep8 mypy pylint

test: export JARR_CONFIG = example_conf/jarr.test.json
test:
	pipenv run nosetests tests/ -vv --with-coverage --cover-package=jarr

build-base:
	docker build . --file Dockerfiles/pythonbase -t jarr-base:latest

start-env:
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		up -d

run-server: export JARR_CONFIG = $(CONF_FILE)
run-server:
	pipenv run gunicorn -c $(GUNICORN_CONF) -b $(SERVER_ADDR):$(SERVER_PORT) wsgi:application

run-worker: export JARR_CONFIG = $(CONF_FILE)
run-worker:
	pipenv run celery worker --app ep_celery.celery_app

create-db:
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		exec postgresql \
		su postgres -c \
		"createuser jarr --no-superuser --createdb --no-createrole"
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		exec postgresql su postgres -c "createdb jarr --no-password"

init-env: export JARR_CONFIG = $(CONF_FILE)
init-env: create-db
	pipenv run ./manager.py db_create
	pipenv run ./manager.py db stamp $(DB_VER)

stop-env:
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		down --remove-orphans

clean-env: stop-env
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		rm --force

status-env:
	pipenv run docker-compose \
		--project-name jarr \
		--file Dockerfiles/dev-env.yml \
		ps
