import unittest
from datetime import datetime, timedelta

from tests.base import conf
from crawler.lib.headers_handling import extract_feed_info, rfc_1123_utc
from lib.utils import utc_now


def assert_in_range(val, ref, sec_range=1):
    low, high = ref - timedelta(seconds=1), ref + timedelta(seconds=1)
    assert low <= val, "%s > %s: diff %ss" % (
            low.isoformat(), val.isoformat(), (val - low).total_seconds())
    assert val <= high, "%s > %s: diff %ss" % (
            val.isoformat(), high.isoformat(), (high - val).total_seconds())


class HeadersHandlingTest(unittest.TestCase):

    def test_defaulting(self):
        self.assertEquals(None, extract_feed_info({})['expires'])

        self.assertEquals(None,
        extract_feed_info({'cache-control': ''})['expires'])
        self.assertEquals(None,
                extract_feed_info({'cache-control': 'garbage'})['expires'])

        self.assertEquals(None,
                extract_feed_info({'expires': ''})['expires'])
        self.assertEquals(None,
                extract_feed_info({'expires': 'garbage'})['expires'])

    def test_extract_max_age(self):
        max_age = conf.FEED_MAX_EXPIRES / 2
        headers = {'cache-control': 'garbage max-age=%d garbage' % max_age}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=max_age))
        headers['expires'] = rfc_1123_utc(delta=timedelta(hours=12))
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=max_age))

    def test_extract_expires(self):
        hours_off = int(conf.FEED_MAX_EXPIRES / 60 / 60)
        headers = {'expires': rfc_1123_utc(delta=timedelta(hours=hours_off))}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(hours=hours_off))

    def test_extract_naive_expires(self):
        ok_delta = timedelta(seconds=conf.FEED_MAX_EXPIRES / 2)
        headers = {'expires': (datetime.utcnow() + ok_delta).isoformat()}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + ok_delta)

    def test_lower_bound(self):
        headers = {'cache-control': 'max-age=%d' % (conf.FEED_MIN_EXPIRES / 2)}
        assert_in_range(extract_feed_info(headers)['expires'],
                utc_now() + (1.5 * timedelta(seconds=conf.FEED_MIN_EXPIRES)))

    def test_upper_bound(self):
        headers = {'cache-control': 'max-age=%d' % (conf.FEED_MAX_EXPIRES * 2)}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=conf.FEED_MAX_EXPIRES))
