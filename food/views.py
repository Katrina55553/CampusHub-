import json
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib import messages
from .models import Category, Shop, Review
from .services.taste import TasteProfile, popular_shops
from .services.analytics import FoodAnalytics
from utils.filters import QueryFilter


# 通用店铺查询过滤器
_SHOP_FILTER = QueryFilter(
    Shop,
    filters={'category': ('category_id', 'exact')},
    search_fields=['name', 'description', 'location'],
    search_param='q',
    default_ordering='-created_at',
)


def home(request):
    """首页：分类导航 + 高分推荐 + 最新店铺"""
    categories = Category.objects.all()
    # 高分店铺（按平均评分降序，取前8个）
    top_shops = Shop.objects.annotate(avg_r=Avg('reviews__rating')).order_by('-avg_r')[:8]
    # 最新店铺
    new_shops = Shop.objects.order_by('-created_at')[:4]

    context = {
        'categories': categories,
        'top_shops': top_shops,
        'new_shops': new_shops,
    }
    return render(request, 'food/home.html', context)


def shop_list(request):
    """全部店铺列表，支持按分类筛选"""
    shops, meta = _SHOP_FILTER.apply(request.GET)
    categories = Category.objects.all()
    current_category = None

    category_id = meta.get('category')
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)

    context = {
        'shops': shops,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'food/shop_list.html', context)


def shop_by_category(request, pk):
    """按分类查看店铺（重定向到列表+筛选参数）"""
    return redirect(f'{reverse("shop_list")}?category={pk}')


def shop_detail(request, pk):
    """店铺详情 + 评价列表"""
    shop = get_object_or_404(Shop, pk=pk)
    reviews = shop.reviews.select_related('user').all()

    context = {
        'shop': shop,
        'reviews': reviews,
    }
    return render(request, 'food/shop_detail.html', context)


def search(request):
    """搜索店铺"""
    shops, meta = _SHOP_FILTER.apply(request.GET)
    context = {
        'shops': shops,
        'query': meta.get('q', ''),
    }
    return render(request, 'food/search.html', context)


@login_required
def add_review(request, pk):
    """添加评价"""
    shop = get_object_or_404(Shop, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content', '').strip()
        
        if not rating or not content:
            messages.error(request, '请填写完整信息')
        elif len(content) > 500:
            messages.error(request, '评价内容不能超过500字')
        else:
            Review.objects.create(
                shop=shop,
                user=request.user,
                rating=int(rating),
                content=content
            )
            FoodAnalytics.invalidate()
            messages.success(request, '评价发表成功！')
    return redirect('shop_detail', pk=pk)


def taste_analysis(request):
    """判别分析：根据用户评分数据判断口味偏好并推荐。"""
    profile = TasteProfile(request.user)

    context = {
        'is_authenticated': request.user.is_authenticated,
        'user_review_count': profile.review_count,
        'user_avg_rating': profile.avg_rating,
        'cat_avg_list': profile.category_avg_list(),
        'taste_tags': profile.taste_tags,
        'recommendations': profile.recommend() if profile.review_count > 0 else Shop.objects.none(),
        'popular_shops': popular_shops(),
    }
    return render(request, 'food/taste_analysis.html', context)


def analytics(request):
    """数据可视化页面"""
    data = FoodAnalytics.snapshot()
    context = {
        'rating_labels': json.dumps(['1星', '2星', '3星', '4星', '5星']),
        'rating_data': json.dumps(data['rating_dist']),
        'pie_labels': json.dumps(data['pie_labels']),
        'pie_data': json.dumps(data['pie_data']),
        'total_reviews': data['total_reviews'],
        'total_shops': data['total_shops'],
        'total_categories': data['total_categories'],
    }
    return render(request, 'food/analytics.html', context)
