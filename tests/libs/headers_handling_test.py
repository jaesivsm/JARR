import unittest
from datetime import datetime, timedelta, UTC

from jarr.crawler.lib.headers_handling import extract_feed_info, rfc_1123_utc
from jarr.bootstrap import conf


def assert_in_range(val, ref, sec=2):
    low, high = ref - timedelta(seconds=sec), ref + timedelta(seconds=sec)
    assert low <= val, "%s > %s: diff %ss" % (
            low.isoformat(), val.isoformat(), (val - low).total_seconds())
    assert val <= high, "%s > %s: diff %ss" % (
            val.isoformat(), high.isoformat(), (high - val).total_seconds())


class HeadersHandlingTest(unittest.TestCase):

    def test_defaulting(self):
        self.assertFalse('expires' in extract_feed_info({}))

        self.assertFalse('expires' in extract_feed_info({'cache-control': ''}))
        self.assertFalse(
                'expires' in extract_feed_info({'cache-control': 'garbage'}))

        self.assertFalse('expires' in extract_feed_info({'expires': ''}))
        self.assertFalse(
                'expires' in extract_feed_info({'expires': 'garbage'}))

    @staticmethod
    def test_extract_max_age():
        max_age = conf.feed.max_expires / 2
        headers = {'cache-control': f"garbage max-age={max_age} garbage"}
        assert_in_range(extract_feed_info(headers)['expires'],
                        datetime.now(UTC) + timedelta(seconds=max_age))
        headers['expires'] = rfc_1123_utc(delta=timedelta(hours=12))
        assert_in_range(extract_feed_info(headers)['expires'],
                        datetime.now(UTC) + timedelta(seconds=max_age))

    @staticmethod
    def test_extract_expires():
        hours_off = int(conf.feed.max_expires / 60 / 60)
        headers = {'expires': rfc_1123_utc(delta=timedelta(hours=hours_off))}
        assert_in_range(extract_feed_info(headers)['expires'],
                        datetime.now(UTC) + timedelta(hours=hours_off))

    @staticmethod
    def test_extract_naive_expires():
        ok_delta = timedelta(seconds=conf.feed.max_expires / 2)
        expires = (datetime.now(UTC) + ok_delta).replace(tzinfo=None)
        headers = {'expires': (expires).isoformat()}
        assert_in_range(extract_feed_info(headers)['expires'],
                        datetime.now(UTC) + ok_delta)
