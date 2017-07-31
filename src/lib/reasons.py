from enum import Enum


class ClusterReason(Enum):
    original = 'original'  # the article is the cluster's original one
    # the article has the same name and share a suitable category
    title = 'title'
    # the article has the same link that the main one of the cluster
    link = 'link'
    tf_idf = 'tf_idf'  # the article has been clustered through tf_idf


class ReadReason(Enum):
    read = 'read'  # the user has read the cluster
    consulted = 'consulted'  # the user was redirected to the cluster
    marked = 'marked'  # the user has marked the cluster as read
    # the cluster was marked as read along with others
    mass_marked = 'mass_marked'
    # the cluster was marked as read by a filter
    filtered = 'filtered'


class CacheReason(Enum):
    status_code_304 = 'status_code_304'  # feeds validate sent cache with 304
    etag = 'etag'  # manual etag check works
    etag_calculated = 'etag_calculated'  # generated etag check works
