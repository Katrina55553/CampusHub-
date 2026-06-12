from django.db import models
from django.contrib.auth.models import User


LOCATIONS = [
    ('nanmen', '南门快递柜'),
    ('beimen', '北门快递站'),
    ('cainiao', '菜鸟驿站'),
    ('yunda', '韵达快递点'),
    ('shunfeng', '顺丰快递点'),
    ('jindong', '京东快递点'),
    ('other', '其他'),
]

STATUSES = [
    ('pending', '待接单'),
    ('accepted', '已接单'),
    ('completed', '已完成'),
    ('cancelled', '已取消'),
]


class Order(models.Model):
    title = models.CharField('包裹简述', max_length=100)
    description = models.TextField('详细描述', blank=True, default='')
    location = models.CharField('快递点', max_length=20, choices=LOCATIONS)
    pickup_code = models.CharField('取件码', max_length=50, blank=True, default='')
    reward = models.DecimalField('报酬金额', max_digits=8, decimal_places=2)
    contact = models.CharField('联系方式', max_length=50)
    status = models.CharField('订单状态', max_length=20, choices=STATUSES, default='pending')
    publisher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_orders', verbose_name='发布者')
    helper = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='helped_orders', verbose_name='接单者')
    accepted_at = models.DateTimeField('接单时间', null=True, blank=True)
    created_at = models.DateTimeField('发布时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '订单'
        verbose_name_plural = '订单'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['publisher']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'
