from datetime import UTC, datetime, timedelta, timezone

from jarr.bootstrap import conf, session
from jarr.controllers import (
    ArticleController,
    ClusterController,
    FeedController,
    IconController,
    UserController,
)
from jarr.controllers.feed_builder import FeedBuilderController
from tests.base import BaseJarrTest
from tests.utils import update_on_all_objs


class FeedControllerTest(BaseJarrTest):
    _contr_cls = FeedController

    def test_delete(self):
        feed_ctrl = FeedController()
        for feed in feed_ctrl.read():
            feed_ctrl.delete(feed.id)
        assert ClusterController(2).read().count() == 0
        assert ArticleController(2).read().count() == 0

    def test_delete_main_cluster_handling(self):
        suffix = "suffix"
        clu = ClusterController().get(id=10)
        acontr = ArticleController(clu.user_id)
        fcontr = FeedController(clu.user_id)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        for art_to_del in acontr.read(
            link=clu.main_article.link, id__ne=clu.main_article.id
        ):
            acontr.delete(art_to_del.id)

        other_feed = fcontr.read(id__ne=clu.main_article.feed_id).first()
        update_on_all_objs(
            articles=[clu.main_article],
            feeds=[other_feed],
            cluster_enabled=True,
        )
        acontr.create(
            feed_id=other_feed.id,
            entry_id=clu.main_article.entry_id + suffix,
            link=clu.main_article.link,
            title=clu.main_article.title + suffix,
            content=clu.main_article.content + suffix,
            date=clu.main_article.date + timedelta(1),
            retrieved_date=clu.main_article.retrieved_date + timedelta(1),
        )

        ClusterController(clu.user_id).clusterize_pending_articles()
        clu = ClusterController().get(id=10)
        assert len(clu.articles) == 2
        fcontr.delete(clu.main_article.feed_id)
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        assert len(new_cluster.articles) == 1
        assert new_cluster.main_title != old_title
        assert new_cluster.main_feed_title != old_feed_title
        assert new_cluster.main_article_id != old_art_id

    def test_delete_cluster_handling(self):
        clu = ClusterController().get(id=10)
        old_title = clu.main_title
        old_feed_title, old_art_id = clu.main_feed_title, clu.main_article_id
        assert len(clu.articles) == 1
        new_cluster = ClusterController(clu.user_id).get(id=clu.id)
        assert len(new_cluster.articles) == 1
        assert old_title == new_cluster.main_title
        assert old_feed_title == new_cluster.main_feed_title
        assert old_art_id == new_cluster.main_article_id

    def test_feed_rights(self):
        feed = FeedController(2).read()[0]
        assert ArticleController().read(feed_id=feed.id).count() == 3
        self._test_controller_rights(
            feed, UserController().get(id=feed.user_id)
        )

    def test_update_cluster_on_change_title(self):
        feed = ClusterController(2).read()[0].main_article.feed
        for cluster in feed.clusters:
            assert feed.title == cluster.main_feed_title
        FeedController(2).update({"id": feed.id}, {"title": "updated title"})

        feed = FeedController(2).get(id=feed.id)
        assert feed.title == "updated title"
        for cluster in feed.clusters:
            assert feed.title == cluster.main_feed_title

    def test_admin_update_cluster_on_change_title(self):
        feed = ClusterController(2).read()[0].main_article.feed
        for cluster in feed.clusters:
            assert feed.title == cluster.main_feed_title
        FeedController().update({"id": feed.id}, {"title": "updated title"})

        feed = FeedController().get(id=feed.id)
        assert feed.title == "updated title"
        for cluster in feed.clusters:
            assert feed.title == cluster.main_feed_title

    def assert_late_count(self, count, msg):
        fctrl = FeedController()
        assert count == len(list(fctrl.list_late())), msg
        assert count == len(fctrl.list_fetchable()), msg

    @staticmethod
    def update_all_no_ctrl(**kwargs):
        for feed in FeedController().read():
            for key, value in kwargs.items():
                setattr(feed, key, value)
            session.add(feed)
        session.commit()

    def assert_in_range(self, low, val, high):
        assert low <= val, f"{low.isoformat()} > {val.isoformat()}"
        assert val <= high, f"{val.isoformat()} > {high.isoformat()}"

    def test_fetchable(self):
        fctrl = FeedController()
        total = fctrl.read().count()
        unix = datetime(1970, 1, 1).replace(tzinfo=timezone.utc)
        count = 0
        for fd in fctrl.list_late():
            count += 1
            assert unix == fd.last_retrieved
            assert unix == fd.expires
        assert total == count

        fetchables = fctrl.list_fetchable()
        now = datetime.now(UTC)
        for fd in fetchables:
            self.assert_in_range(
                now - timedelta(seconds=1), fd.last_retrieved, now
            )
            self.assertEqual(unix, fd.expires)
        self.assert_late_count(
            0, "no late feed to report because all just fetched"
        )
        fctrl.update({}, {"expires": unix})
        for fd in fctrl.read():  # expires should be corrected
            self.assert_in_range(
                now + timedelta(seconds=conf.feed.min_expires - 1),
                fd.expires,
                now + timedelta(seconds=conf.feed.min_expires + 1),
            )

        lr_not_matter = timedelta(seconds=conf.feed.min_expires + 10)
        self.update_all_no_ctrl(
            expires=now - timedelta(seconds=1),
            last_retrieved=now - lr_not_matter,
        )
        self.assert_late_count(total, "all feed just expired")
        self.update_all_no_ctrl(expires=now + timedelta(seconds=1))
        self.assert_late_count(
            0, "all feed will expire in a second, none are expired"
        )

    def _test_fetching_anti_herding_mech(self, now):
        fctrl = FeedController()
        total = fctrl.read().count()

        half = timedelta(seconds=conf.feed.min_expires / 2)
        twice = timedelta(seconds=conf.feed.min_expires * 2)
        long_ago = timedelta(seconds=conf.feed.max_expires * 2)

        self.update_all_no_ctrl(expires=now + half, last_retrieved=now)
        self.assert_late_count(0, "all have just been retrieved, none expired")
        self.update_all_no_ctrl(expires=now - twice, last_retrieved=now - half)
        self.assert_late_count(0, "have been retrieved not too long ago")

        self.update_all_no_ctrl(
            expires=now + twice, last_retrieved=now - long_ago
        )
        self.assert_late_count(
            total, "all retrieved some time ago, not expired"
        )

    def test_fetching_anti_herding_mech_utctimezone(self):
        self._test_fetching_anti_herding_mech(datetime.now(UTC))

    def test_fetching_anti_herding_mech_utcplustwelve(self):
        self._test_fetching_anti_herding_mech(
            utc_now().astimezone(timezone(timedelta(hours=12)))
        )

    def test_icon_url_normalization_with_unicode(self):
        """Test that icon URL encoding is normalized to match database"""
        icon_ctrl = IconController()
        feed_ctrl = FeedController(2)

        # Test URL with Unicode characters (like légrandcontinent)
        # This simulates the issue where the URL has special characters
        test_icon_url = (
            "https://legrandcontinent.eu/fr/wp-content/uploads/sites/2/2021"
            "/03/cropped-Capture-décran-2021-03-20-à-19.21.51-32x32.png"
        )

        # Create feed data with icon_url
        feed_data = {
            "title": "Test Feed with Unicode Icon",
            "link": "https://legrandcontinent.eu/fr/feed/",
            "site_link": "https://legrandcontinent.eu/fr/",
            "icon_url": test_icon_url,
        }

        # Create the feed - this should handle icon URL normalization
        feed = feed_ctrl.create(**feed_data)

        # Verify feed was created
        assert feed is not None
        assert feed.title == "Test Feed with Unicode Icon"
        assert feed.icon_url is not None

        # Verify the icon exists in database with the normalized URL
        icon = icon_ctrl.read(url=feed.icon_url).first()
        assert icon is not None, "Icon should exist in database"
        assert (
            feed.icon_url == icon.url
        ), "Feed icon_url should match icon URL in database"

    def test_feedbuilder_and_feed_creation_legrandcontinent(self):
        """Integration test for feedbuilder + feed creation with legrandcontinent"""
        url = "legrandcontinent.eu/fr"

        # Step 1: Use FeedBuilder to construct feed data
        fbc = FeedBuilderController(url)
        feed_data = fbc.construct()

        # Verify feedbuilder worked
        assert "link" in feed_data
        assert "title" in feed_data
        assert "icon_url" in feed_data

        # Step 2: Filter feed data like the API does
        # The API uses parse_meaningful_params which only keeps fields defined in the parser
        # Remove UI-only fields that aren't part of the Feed model
        feed_create_data = {
            k: v
            for k, v in feed_data.items()
            if k
            not in ["links", "same_link_count"]  # These are UI-only fields
        }

        # Step 3: Create the feed
        feed_ctrl = FeedController(2)
        feed = feed_ctrl.create(**feed_create_data)

        # Verify feed was created successfully
        assert feed
        assert feed.id
        assert feed.link == feed_data["link"]
        assert feed.icon_url is not None

        # Verify icon exists in database with normalized URL
        icon_ctrl = IconController()
        icon = icon_ctrl.read(url=feed.icon_url).first()
        assert icon, "Icon should exist in database after feed creation"
        assert (
            feed.icon_url == icon.url
        ), "Feed icon_url should match icon URL in database"
