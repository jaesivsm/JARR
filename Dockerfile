FROM python:3.5-slim

ARG VERSION=master

COPY docker_files/logging.ini /etc/jarr_logging.ini
COPY docker_files/gunicorn.py /etc/gunicorn.py
RUN echo "deb http://deb.debian.org/debian jessie main" >> /etc/apt/source.list && apt-get update && apt-get install -y git wget
# Retrieving JARR code
RUN git clone --quiet https://github.com/jaesivsm/JARR.git /jarr && \
cd /jarr && git checkout ${VERSION} && git submodule --quiet update --init
WORKDIR /jarr
# Installing python dependencies
RUN pip install -r requirements.txt -r requirements.postgres.txt --upgrade gunicorn json-logging-py && \
python -c "import nltk; nltk.download('all')"
# Building Node bundle
RUN wget --quiet https://deb.nodesource.com/setup_9.x --output-document=npm_install; \
bash npm_install; \
apt-get install -y nodejs; \
npm install && npm run build; \
rm -rf node_modules npm_install; \
apt-get purge -y --purge nodejs; apt-get autoremove -y
# Mount so your configuration is accessible from here
VOLUME /etc/
EXPOSE 8000
CMD ["/usr/local/bin/gunicorn", "--config", "/etc/gunicorn.py", "--log-config", "/etc/jarr_logging.ini", "-b", "0.0.0.0:8000", "wsgi:application"]
