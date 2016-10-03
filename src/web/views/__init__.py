from web.views import views, home, session_mgmt, api
from web.views.article import articles_bp
from web.views.cluster import cluster_bp
from web.views.feed import feed_bp, feeds_bp
from web.views.icon import icon_bp
from web.views.admin import admin_bp
from web.views.user import user_bp, users_bp

__all__ = ['views', 'home', 'session_mgmt', 'api',
           'articles_bp', 'cluster_bp', 'feed_bp', 'feeds_bp',
           'icon_bp', 'admin_bp', 'user_bp', 'users_bp']
