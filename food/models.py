from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import User


class Category(models.Model):
    """美食分类：食堂、奶茶、小吃、火锅..."""
    name = models.CharField(max_length=50, verbose_name='分类名称')
    icon = models.CharField(max_length=50, default='bi-shop', verbose_name='Bootstrap图标类名')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '美食分类'
        verbose_name_plural = '美食分类'
        ordering = ['id']

    def __str__(self):
        return self.name


class Shop(models.Model):
    """店铺"""
    name = models.CharField(max_length=100, verbose_name='店铺名称')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='所属分类')
    image = models.ImageField(upload_to='shops/', default='shops/default.jpg', verbose_name='店铺图片')
    location = models.CharField(max_length=200, verbose_name='位置')
    description = models.TextField(blank=True, verbose_name='描述')
    avg_price = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name='人均价格')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def avg_rating(self):
        """计算平均评分"""
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else 0

    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    """用户评价"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews', verbose_name='店铺')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    rating = models.IntegerField(choices=[(i, f'{i}星') for i in range(1, 6)], verbose_name='评分')
    content = models.TextField(verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')

    class Meta:
        verbose_name = '用户评价'
        verbose_name_plural = '用户评价'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shop', 'user']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.shop.name} - {self.rating}星'
