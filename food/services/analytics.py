"""美食模块数据聚合服务：封装 analytics 视图的统计与缓存逻辑。"""

from django.core.cache import cache
from django.db.models import Count

from ..models import Category, Review, Shop


class FoodAnalytics:
    """提供美食模块统计快照，结果按 TTL 缓存。"""

    CACHE_KEY = 'food:analytics'
    TTL = 300  # 5 分钟

    @classmethod
    def snapshot(cls):
        data = cache.get(cls.CACHE_KEY)
        if data is not None:
            return data
        data = cls._compute()
        cache.set(cls.CACHE_KEY, data, cls.TTL)
        return data

    @classmethod
    def invalidate(cls):
        cache.delete(cls.CACHE_KEY)

    @classmethod
    def _compute(cls):
        rating_dist = [0] * 5
        for row in Review.objects.values('rating').annotate(count=Count('id')):
            if 1 <= row['rating'] <= 5:
                rating_dist[row['rating'] - 1] = row['count']

        pie_rows = (
            Shop.objects.values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return {
            'rating_dist': rating_dist,
            'pie_labels': [r['category__name'] for r in pie_rows],
            'pie_data': [r['count'] for r in pie_rows],
            'total_reviews': Review.objects.count(),
            'total_shops': Shop.objects.count(),
            'total_categories': Category.objects.count(),
        }
