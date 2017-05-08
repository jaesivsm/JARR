from lib.integrations.abstract import add_integration, dispatch
from lib.integrations.mercury import MercuryIntegration
from lib.integrations.reddit import RedditIntegration
from lib.integrations.youtube import YoutubeIntegration
from lib.integrations.koreus import KoreusIntegration
from lib.integrations.rss_bridge import InstagramIntegration


add_integration(MercuryIntegration())
add_integration(RedditIntegration())
add_integration(YoutubeIntegration())
add_integration(KoreusIntegration())
add_integration(InstagramIntegration())


__all__ = ['dispatch']
