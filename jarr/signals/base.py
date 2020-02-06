from blinker import signal

feed_creation = signal('feed_creation')
article_parsing = signal('article_parsing')
entry_parsing = signal('entry_parsing')
