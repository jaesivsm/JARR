from datetime import datetime, timezone

UNIX_START = datetime(1970, 1, 1, tzinfo=timezone.utc)
MIMETYPES = (('application/feed+json', 1),
             ('application/atom+xml', 1),
             ('application/rss+xml', 1),
             ('application/rdf+xml', 0.9),
             ('application/xml', 0.8),
             ('application/json', 0.8),
             ('text/xml', 0.6),
             ('*/*', 0.2))

FEED_ACCEPT_HEADERS = ','.join(mtype + (';q=%0.1f' % qual if qual < 1 else '')
                               for mtype, qual in MIMETYPES)
FEED_MIMETYPES = [mtype for mtype, quality in MIMETYPES if quality >= 0.5]
REQUIRED_JSON_FEED = {'version', 'title'}
GOOGLE_BOT_UA = ("Mozilla/5.0 (compatible; Googlebot/2.1; "
                 "+http://www.google.com/bot.html)")
