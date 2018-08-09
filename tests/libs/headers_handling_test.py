import unittest
from datetime import datetime, timedelta

from tests.base import conf
from jarr_crawler.lib.headers_handling import extract_feed_info, rfc_1123_utc
from jarr_common.utils import utc_now


def assert_in_range(val, ref, sec_range=1):
    low, high = ref - timedelta(seconds=1), ref + timedelta(seconds=1)
    assert low <= val, "%s > %s: diff %ss" % (
            low.isoformat(), val.isoformat(), (val - low).total_seconds())
    assert val <= high, "%s > %s: diff %ss" % (
            val.isoformat(), high.isoformat(), (high - val).total_seconds())


class HeadersHandlingTest(unittest.TestCase):

    def test_defaulting(self):
        self.assertEqual(None, extract_feed_info({})['expires'])

        self.assertEqual(None,
        extract_feed_info({'cache-control': ''})['expires'])
        self.assertEqual(None,
                extract_feed_info({'cache-control': 'garbage'})['expires'])

        self.assertEqual(None,
                extract_feed_info({'expires': ''})['expires'])
        self.assertEqual(None,
                extract_feed_info({'expires': 'garbage'})['expires'])

    def test_extract_max_age(self):
        max_age = conf.feed.max_expires / 2
        headers = {'cache-control': 'garbage max-age=%d garbage' % max_age}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=max_age))
        headers['expires'] = rfc_1123_utc(delta=timedelta(hours=12))
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=max_age))

    def test_extract_expires(self):
        hours_off = int(conf.feed.max_expires / 60 / 60)
        headers = {'expires': rfc_1123_utc(delta=timedelta(hours=hours_off))}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(hours=hours_off))

    def test_extract_naive_expires(self):
        ok_delta = timedelta(seconds=conf.feed.max_expires / 2)
        headers = {'expires': (datetime.utcnow() + ok_delta).isoformat()}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + ok_delta)

    def test_lower_bound(self):
        headers = {'cache-control': 'max-age=%d' % (conf.feed.min_expires / 2)}
        assert_in_range(extract_feed_info(headers)['expires'],
                utc_now() + timedelta(seconds=conf.feed.min_expires * 1.2))

    def test_upper_bound(self):
        headers = {'cache-control': 'max-age=%d' % (conf.feed.max_expires * 2)}
        assert_in_range(extract_feed_info(headers)['expires'],
                        utc_now() + timedelta(seconds=conf.feed.max_expires))
