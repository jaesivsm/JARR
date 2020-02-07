from enum import Enum


class FeedType(Enum):
    classic = 'classic'
    json = 'json'
    tumblr = 'tumblr'
    instagram = 'instagram'
    soundcloud = 'soundcloud'
    reddit = 'reddit'
    fetch = 'fetch'


class ArticleDisplayType(Enum):
    text = 'text'
    image = 'image'
    video = 'video'


class ArticleType(Enum):
    classic = 'classic'
    youtube = 'youtube'
    koreus = 'koreus'
    reddit = 'reddit'
