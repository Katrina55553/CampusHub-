"""快递模块统计服务：封装 stats 视图的聚合计算与缓存。"""

from statistics import mean, median, stdev

from django.core.cache import cache
from django.db.models import Avg, Count

from ..models import Order, LOCATIONS


class OrderStats:
    """提供订单统计快照，结果按 TTL 缓存。"""

    CACHE_KEY = 'orders:stats'
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
        orders = Order.objects.all()
        rewards = list(orders.values_list('reward', flat=True))

        reward_stats = {}
        if rewards:
            sorted_rewards = sorted(rewards)
            n = len(sorted_rewards)
            reward_stats = {
                'count': n,
                'sum': round(sum(sorted_rewards), 2),
                'mean': round(mean(sorted_rewards), 2),
                'median': round(median(sorted_rewards), 2),
                'std': round(stdev(sorted_rewards), 2) if n > 1 else 0,
                'min': min(sorted_rewards),
                'max': max(sorted_rewards),
            }

        status_counts = dict(
            orders.values_list('status').annotate(c=Count('id')).values_list('status', 'c')
        )

        location_data = list(
            orders.values('location')
            .annotate(count=Count('id'), avg_reward=Avg('reward'))
            .order_by('-count')
        )

        return {
            'rewards': rewards,
            'reward_stats': reward_stats,
            'status_counts': status_counts,
            'location_data': location_data,
            'total_orders': orders.count(),
        }
