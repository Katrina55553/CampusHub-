from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import Order
from .services.lifecycle import (
    accept_order,
    cancel_order,
    complete_order,
    OrderLifecycleError,
)
from .services.stats import OrderStats
from utils.filters import QueryFilter


class OrderLifecycleServiceTests(TestCase):
    def setUp(self):
        self.publisher = User.objects.create_user(username='pub', password='pw')
        self.helper = User.objects.create_user(username='helper', password='pw')
        self.order = Order.objects.create(
            title='快递',
            location='nanmen',
            reward='3.00',
            contact='wx',
            publisher=self.publisher,
        )

    def test_accept_order(self):
        order = accept_order(self.order.id, self.helper)
        self.assertEqual(order.status, 'accepted')
        self.assertEqual(order.helper, self.helper)
        self.assertIsNotNone(order.accepted_at)

    def test_publisher_cannot_accept_own_order(self):
        with self.assertRaises(OrderLifecycleError):
            accept_order(self.order.id, self.publisher)

    def test_complete_order_only_by_publisher(self):
        accept_order(self.order.id, self.helper)
        order = complete_order(self.order.id, self.publisher)
        self.assertEqual(order.status, 'completed')

    def test_helper_cannot_complete_order(self):
        accept_order(self.order.id, self.helper)
        with self.assertRaises(OrderLifecycleError):
            complete_order(self.order.id, self.helper)

    def test_cancel_order(self):
        order = cancel_order(self.order.id, self.publisher)
        self.assertEqual(order.status, 'cancelled')


class OrderStatsServiceTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='u', password='pw')
        Order.objects.create(title='A', location='nanmen', reward='2.00', contact='wx', publisher=self.user)
        Order.objects.create(title='B', location='beimen', reward='4.00', contact='wx', publisher=self.user)

    def test_snapshot_returns_stats(self):
        data = OrderStats.snapshot()
        self.assertEqual(data['total_orders'], 2)
        self.assertEqual(data['reward_stats']['count'], 2)

    def test_cache_is_used(self):
        OrderStats.snapshot()
        Order.objects.create(title='C', location='nanmen', reward='6.00', contact='wx', publisher=self.user)
        cached = OrderStats.snapshot()
        self.assertEqual(cached['total_orders'], 2)

        OrderStats.invalidate()
        fresh = OrderStats.snapshot()
        self.assertEqual(fresh['total_orders'], 3)


class OrderQueryFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u2', password='pw')
        self.order = Order.objects.create(
            title='中通快递', description='小包裹', location='nanmen', reward='3.00', contact='wx', publisher=self.user
        )

    def test_filter_by_status(self):
        f = QueryFilter(
            Order,
            filters={
                'status': lambda qs, value, meta: qs.filter(status=value) if value in ('pending', 'accepted') else qs
            },
        )
        qs, meta = f.apply({'status': 'pending'})
        self.assertEqual(list(qs), [self.order])

    def test_search_by_title(self):
        f = QueryFilter(Order, search_fields=['title', 'description'])
        qs, meta = f.apply({'q': '中通'})
        self.assertEqual(list(qs), [self.order])
