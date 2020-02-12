from enum import Enum


class FeedType(Enum):
    classic = 'classic'
    json = 'json'
    tumblr = 'tumblr'
    instagram = 'instagram'
    soundcloud = 'soundcloud'
    reddit = 'reddit'
    fetch = 'fetch'
    koreus = 'koreus'


class ArticleType(Enum):
    text = 'text'
    image = 'image'
    video = 'video'
