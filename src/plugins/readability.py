import logging
import requests
from urllib.parse import urlencode


logger = logging.getLogger(__name__)
READABILITY_PARSER = 'https://www.readability.com/api/content/v1/parser?'


def parse(url, key):
    response = requests.get(
                READABILITY_PARSER + urlencode({'url': url, 'token': key}))
    response.raise_for_status()
    return response.json()['content']
