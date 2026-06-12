#!/usr/bin/env python
"""创建测试数据"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from food.models import Category, Shop

# 创建分类
categories_data = [
    {'name': '食堂窗口', 'icon': 'bi-building'},
    {'name': '奶茶饮品', 'icon': 'bi-cup-hot'},
    {'name': '小吃快餐', 'icon': 'bi-egg-fried'},
    {'name': '火锅烧烤', 'icon': 'bi-fire'},
    {'name': '面包甜品', 'icon': 'bi-cake2'},
]

categories = {}
for data in categories_data:
    cat, created = Category.objects.get_or_create(name=data['name'], defaults={'icon': data['icon']})
    categories[data['name']] = cat
    if created:
        print(f"创建分类: {cat.name}")

# 创建店铺
shops_data = [
    {
        'name': '学一食堂麻辣香锅',
        'category': '食堂窗口',
        'location': '第一食堂二楼',
        'description': '麻辣鲜香，食材新鲜，分量十足。招牌麻辣香锅，搭配各种蔬菜和肉类，满足你的味蕾。',
        'avg_price': 18.0,
    },
    {
        'name': '益禾堂',
        'category': '奶茶饮品',
        'location': '学生街B12',
        'description': '新鲜水果茶，手工制作，口感清爽。推荐招牌益禾烤奶。',
        'avg_price': 10.0,
    },
    {
        'name': '校门口炸鸡',
        'category': '小吃快餐',
        'location': '南门小吃街5号',
        'description': '外酥里嫩，香气扑鼻。招牌炸鸡腿，搭配秘制酱料，回味无穷。',
        'avg_price': 15.0,
    },
    {
        'name': '川味火锅',
        'category': '火锅烧烤',
        'location': '北门商业街2楼',
        'description': '正宗川味火锅，麻辣鲜香，锅底浓郁。食材新鲜，种类丰富。',
        'avg_price': 50.0,
    },
    {
        'name': '幸福西饼',
        'category': '面包甜品',
        'location': '学生街A5',
        'description': '手工烘焙，新鲜出炉。招牌蛋糕、面包、甜点，满足你的甜蜜需求。',
        'avg_price': 25.0,
    },
    {
        'name': '学二食堂面食',
        'category': '食堂窗口',
        'location': '第二食堂一楼',
        'description': '手工拉面，劲道爽滑。牛肉面、炸酱面、西红柿鸡蛋面，各种口味任你选。',
        'avg_price': 12.0,
    },
    {
        'name': '蜜雪冰城',
        'category': '奶茶饮品',
        'location': '南门商业街',
        'description': '高性价比奶茶，柠檬水、冰淇淋、奶茶，价格实惠，口味不错。',
        'avg_price': 8.0,
    },
    {
        'name': '黄焖鸡米饭',
        'category': '小吃快餐',
        'location': '东门小吃街',
        'description': '黄焖鸡米饭，鸡肉嫩滑，汤汁浓郁，搭配米饭，简单美味。',
        'avg_price': 16.0,
    },
]

for data in shops_data:
    shop, created = Shop.objects.get_or_create(
        name=data['name'],
        defaults={
            'category': categories[data['category']],
            'location': data['location'],
            'description': data['description'],
            'avg_price': data['avg_price'],
        }
    )
    if created:
        print(f"创建店铺: {shop.name}")

print("\n测试数据创建完成！")
print(f"分类数量: {Category.objects.count()}")
print(f"店铺数量: {Shop.objects.count()}")
