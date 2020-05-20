import re

from bs4 import BeautifulSoup
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import TSVECTOR


def to_vector(title=None, tags=None, content=None, parsing_result=None):
    parsing_result = parsing_result or {}
    title = parsing_result.get('title', title) or ''
    tags = parsing_result.get('tags', tags) or []
    content = parsing_result.get('parsed_content', content) or ''
    vector = ' '.join([title, ' '.join(tags), content])
    vector = BeautifulSoup(vector, 'html.parser').text
    vector = re.sub(r'\W', ' ', vector).strip()
    if vector:
        return cast(vector, TSVECTOR)
