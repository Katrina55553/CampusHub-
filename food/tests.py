from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User
from django.core.cache import cache

from .models import Category, Shop, Review
from .services.taste import TasteProfile, popular_shops
from .services.analytics import FoodAnalytics
from utils.filters import QueryFilter


class TasteProfileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='taster', password='testpass123')
        self.cat = Category.objects.create(name='奶茶', icon='bi-cup')
        self.shop = Shop.objects.create(
            name='一点点',
            category=self.cat,
            location='食堂一楼',
            description='奶茶',
            avg_price=15,
        )

    def test_empty_profile_for_anonymous(self):
        profile = TasteProfile(AnonymousUser())
        self.assertEqual(profile.review_count, 0)
        self.assertEqual(profile.taste_tags, [])

    def test_profile_builds_tags_and_recommendations(self):
        Review.objects.create(shop=self.shop, user=self.user, rating=5, content='好喝')
        profile = TasteProfile(self.user)

        self.assertEqual(profile.review_count, 1)
        self.assertEqual(profile.avg_rating, 5.0)
        self.assertIn('「奶茶」忠实爱好者', profile.taste_tags)
        # 已评价过的店铺不应被推荐
        self.assertEqual(list(profile.recommend()), [])

    def test_popular_shops_returns_rated_shops(self):
        Review.objects.create(shop=self.shop, user=self.user, rating=5, content='好喝')
        shops = popular_shops()
        self.assertIn(self.shop, list(shops))


class FoodAnalyticsServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.cat = Category.objects.create(name='小吃', icon='bi-shop')
        self.shop = Shop.objects.create(name='烤冷面', category=self.cat, location='南门')
        self.user = User.objects.create_user(username='u1', password='pw')
        Review.objects.create(shop=self.shop, user=self.user, rating=4, content='不错')

    def test_snapshot_caches_data(self):
        first = FoodAnalytics.snapshot()
        self.assertEqual(first['total_reviews'], 1)

        Review.objects.create(shop=self.shop, user=self.user, rating=5, content='很好')
        cached = FoodAnalytics.snapshot()
        # 缓存未失效，仍返回旧数据
        self.assertEqual(cached['total_reviews'], 1)

        FoodAnalytics.invalidate()
        fresh = FoodAnalytics.snapshot()
        self.assertEqual(fresh['total_reviews'], 2)


class ShopQueryFilterTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name='火锅', icon='bi-fire')
        self.shop = Shop.objects.create(name='海底捞', category=self.cat, location='北门')

    def test_filter_by_category(self):
        f = QueryFilter(Shop, filters={'category': ('category_id', 'exact')})
        qs, meta = f.apply({'category': str(self.cat.id)})
        self.assertEqual(list(qs), [self.shop])

    def test_search_by_name(self):
        f = QueryFilter(Shop, search_fields=['name', 'description'])
        qs, meta = f.apply({'q': '海底捞'})
        self.assertEqual(list(qs), [self.shop])
