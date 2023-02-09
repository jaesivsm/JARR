## Installation procedure

It is advised to used the Docker images `jaesivsm/jarr-server` and `jaesivsm/jarr-worker`. However, the `jaesivsm/jarr-front` is build with the address of the production server as API URL. You'll then to rebuild it.

You can take inspiration in [`Dockerfiles/prod-example.yml`](https://github.com/jaesivsm/JARR/blob/master/Dockerfiles/dev-env.yml) which will provide you a working instance of JARR.

### Prerquisite

To run JARR you'll need at least [Docker](https://docs.docker.com/get-docker/) installed.

You'll also need [pipenv](https://github.com/pypa/pipenv#installation) even if there are undocumented ways around that.

## Running the code

```shell
# first clone the repository
git clone https://github.com/jaesivsm/JARR.git

# then copy Dockerfiles/prod-example.yml and edit it to your liking
# for the documentation here, we'll say that you use the example one

# first get inside the cloned repo
cd JARR

# ensure you have the proper packages installed
pipenv sync --dev

# Build base image for server and workers
make build-base

# bring up env
# /!\ You'll want to edit the example proposed below :
#  * have your own configurations file in a directory of you're own
#  * specify a proper directory for postgres to store your data in
make start-env COMPOSE_FILE=Dockerfiles/prod-example.yml

# create database inside the running postgres
# /!\ this command is for test purpose and create db and user without password
# you'll want to change that in production
make db-bootstrap-user COMPOSE_FILE=Dockerfiles/prod-example.yml
make db-bootstrap-tables COMPOSE_FILE=Dockerfiles/prod-example.yml

# create JARR tables
# /!\ this step will fail if you leave the default value for Database address,
# you'll want to replace it with "postgresql" in the jarr.json configuration file
make init-env-docker COMPOSE_FILE=Dockerfiles/prod-example.yml
```

Once finished, you may access jarr on `http://localhost:8501/` and login with `admin:admin`.

## Maintenance

Some tasks will require you to run commands on either the server or the worker :

#### Starting the scheduler

To start the scheduler that'll run all background processing, run :

```
docker-compose --file Dockerfiles/prod-example.yml exec jarr-worker pipenv run python3
```

Then in the python terminal

```python
from jarr.crawler.main import scheduler
scheduler.apply_async()
```

#### Executing Schema and Data migration

```
docker-compose --file Dockerfiles/prod-example.yml exec jarr-worker flask db upgrade
```
