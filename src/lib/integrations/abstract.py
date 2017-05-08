_INTEGRATION_MAPPING = []


class AbstractIntegration:
    """This class provides basic ABI for special integration.

    How does it work:
    When you call on the dispatch method below with an integration type you
    want to apply

    >>> dispatch('feed_creation', feed)

    for earch of the registered integration the dispatch method will test
    if the integration applies by executing the match_<name of the integraiton>
    If it does apply, then the actual integration in called on.

    'match_' methods and integration methods should have the same prototype.
    The match_ method should return true or false wether to call the
    integration method or not.
    If after all the integration method does not change the passed arguments
    it should return False, True otherwise. Objects are expected to be
    changed by reference.
    """

    def match_feed_creation(self, feed, **kwargs):
        """Wether or not to call on 'feed_creation"

        feed: a dict
        """
        return False

    def feed_creation(self, feed, **kwargs):
        """Apply extra treatment to a feed before it's very creation."""
        raise NotImplementedError()

    def match_entry_parsing(self, feed, entry):
        """Wether or not to call on 'entry_parsing'

        feed: a dict
        article: a dict
        """
        return False

    def entry_parsing(self, feed, entry):
        """Very light treatment applied to an entry directly out the rss feed.
        It'll be called each time the crawler encounter an article.

        feed: a dict
        entry: a dict from feed feedparser
        """
        raise NotImplementedError()

    def match_article_parsing(self, user, feed, cluster, **kwargs):
        """Wether or not to call on 'article_parsing'

        user: db obj
        feed: db obj
        cluster: db obj
        """
        return False

    def article_parsing(self, user, feed, cluster, **kwargs):
        "Heavy parsing of an article on user demand."
        raise NotImplementedError()


def add_integration(integration, priority=5):
    priority = int(priority)
    assert isinstance(integration, AbstractIntegration)
    _INTEGRATION_MAPPING.append((integration, priority))
    _INTEGRATION_MAPPING.sort(key=lambda tple: tple[1])


def dispatch(method_name, *args, **kwargs):
    for integration, _ in _INTEGRATION_MAPPING:
        if getattr(integration, 'match_' + method_name)(*args, **kwargs):
            return getattr(integration, method_name)(*args, **kwargs)
