_INTEGRATION_MAPPING = []


class AbstractIntegration:

    @staticmethod
    def match_feed_creation(user, feed, **kwargs):
        return True

    @staticmethod
    def feed_creation(user, feed, **kwargs):
        return feed

    @staticmethod
    def match_article_parsing(user, feed, cluster, **kwargs):
        return True

    @staticmethod
    def article_parsing(user, feed, cluster, **kwargs):
        pass


def add_integration(integration, priority=5):
    priority = int(priority)
    assert isinstance(integration, AbstractIntegration)
    _INTEGRATION_MAPPING.append((integration, priority))
    _INTEGRATION_MAPPING.sort(key=lambda tple: tple[1])


def dispatch(method_name, *args, **kwargs):
    for integration, _ in _INTEGRATION_MAPPING + [(AbstractIntegration, None)]:
        if getattr(integration, 'match_' + method_name)(*args, **kwargs):
            return getattr(integration, method_name)(*args, **kwargs)
