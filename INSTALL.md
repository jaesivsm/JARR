## Installation procedure

It is advised to used the Docker images `jaesivsm/jarr-server` and `jaesivsm/jarr-worker`. However, the `jaesivsm/jarr-front` is build with the address of the production server as API URL. You'll then to rebuild it.

You can take inspiration in [`Dockerfiles/prod.yml`](https://github.com/jaesivsm/JARR/blob/master/Dockerfiles/dev-env.yml) which will provide you a working instance of JARR.

```shell
# first clone the repository
git clone git@github.com:jaesivsm/JARR.git

# then copy Dockerfiles/prod.yml and edit it to your liking
# for the documentation here, we'll say that you use the example one

# bring up env
make start-env COMPOSE_FILE=Dockerfiles/prod.yml

# create database inside the running postgres
# /!\ this command is for test purpose and create db and user without password
# you'll want to change that in production
make create-db COMPOSE_FILE=Dockerfiles/prod.yml

# create JARR tables
make init-env COMPOSE_FILE=Dockerfiles/prod.yml
```
## Maintenance

Some tasks will require you to run commands on either the server or the worker :

### Starting the scheduler

To start the scheduler that'll run all background processing, run :

```
docker-compose --file Dockerfiles/prod.yml exec jarr-worker pipenv run python3
```

Then in the python terminal

```python
from jarr.crawler.main import scheduler
scheduler.apply_async()
```

### Executing Schema and Data migration

```
docker-compose --file Dockerfiles/prod.yml exec jarr-worker ./manager.py db upgrade
```
