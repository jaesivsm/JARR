import unittest
from jarr.models.feed import Feed
from jarr.crawler.article_builders.koreus import KoreusArticleBuilder

CONTENT = """<a href="https://www.koreus.com/video/molly-cavailli-mordu-requin\
.html"><img align="left" alt="vidéo requin citron cage actrice porno femme \
morsure sang pied" class="thumb" hspace="10" src="https://koreus.cdn.li/thumbs\
/201705/molly-cavailli-mordu-requin.jpg" style="max-width:800px"/></a><br/>L'a\
ctrice <a href="https://www.koreus.com/tag/porno">porno</a> Molly Cavalli  fai\
sait un live sous-marin dans une cage quand elle a été mordue par un requin.<b\
r clear="all"/><br/><ul><li>Vidéo (1mn15s) : <a href="https://www.koreus.com/v\
ideo/molly-cavailli-mordu-requin.html"><img src="https://koreus.cdn.li/static/\
images/download.png" style="vertical-align:bottom"/> La pornstar Molly Cavalli\
mordu par un requin-citron</a></li></ul><br/> <p>Cet article <a href="https://\
www.koreus.com/modules/news/article24051.html">L&amp;apos;actrice porno Molly \
Cavalli mordue au pied par un requin-citron (Floride)</a> est apparu en premie\
r sur <a href="http://www.koreus.com">Koreus.com</a>.</p><div class="feedflare\
">+<a href="http://feeds.feedburner.com/~ff/Koreus-articles?a=NC7qqxF2oSM:73v4\
rAjQ_zY:yIl2AUoC8zA"><img border="0" src="http://feeds.feedburner.com/~ff/Kore\
us-articles?d=yIl2AUoC8zA"/></a> <a href="http://feeds.feedburner.com/~ff/Kore\
us-articles?a=NC7qqxF2oSM:73v4rAjQ_zY:F7zBnMyn0Lo"><img border="0" src="http:/\
/feeds.feedburner.com/~ff/Koreus-articles?i=NC7qqxF2oSM:73v4rAjQ_zY:F7zBnMyn0L\
o"/></a> <a href="http://feeds.feedburner.com/~ff/Koreus-articles?a=NC7qqxF2oS\
M:73v4rAjQ_zY:V_sGLiPBpWU"><img border="0" src="http://feeds.feedburner.com/~f\
f/Koreus-articles?i=NC7qqxF2oSM:73v4rAjQ_zY:V_sGLiPBpWU"/></a> <a href="http:/\
/feeds.feedburner.com/~ff/Koreus-articles?a=NC7qqxF2oSM:73v4rAjQ_zY:I9og5sOYxJ\
I"><img border="0" src="http://feeds.feedburner.com/~ff/Koreus-articles?d=I9og\
5sOYxJI"/></a>+</div>"""


class KoreusIntegrationTest(unittest.TestCase):
    link = 'https://www.koreus.com/video/molly-cavailli-mordu-requin.html'
    comments = 'https://www.koreus.com/modules/news/article24051.html'

    def test_entry_parsing(self):
        feed = Feed(link='https://feeds.feedburner.com/Koreus-articles')
        entry = {'summary_detail': {'value': CONTENT}, 'link': self.comments}
        builder = KoreusArticleBuilder(feed, entry, {})
        self.assertEqual(builder.article['link'], self.link)
        self.assertEqual(builder.article['comments'], self.comments)
