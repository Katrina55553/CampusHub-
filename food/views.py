import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.contrib import messages
from .models import Category, Shop, Review


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
    category_id = request.GET.get('category')
    shops = Shop.objects.all()
    current_category = None

    if category_id:
        shops = shops.filter(category_id=category_id)
        current_category = get_object_or_404(Category, id=category_id)

    categories = Category.objects.all()

    context = {
        'shops': shops,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'food/shop_list.html', context)


def shop_by_category(request, pk):
    """按分类查看店铺（重定向到列表+筛选参数）"""
    return redirect(f'/shops/?category={pk}')


def shop_detail(request, pk):
    """店铺详情 + 评价列表"""
    shop = get_object_or_404(Shop, pk=pk)
    reviews = shop.reviews.all()

    context = {
        'shop': shop,
        'reviews': reviews,
    }
    return render(request, 'food/shop_detail.html', context)


def search(request):
    """搜索店铺"""
    q = request.GET.get('q', '')
    shops = Shop.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q) | Q(location__icontains=q)
    ) if q else Shop.objects.none()

    context = {
        'shops': shops,
        'query': q,
    }
    return render(request, 'food/search.html', context)


@login_required
def add_review(request, pk):
    """添加评价"""
    shop = get_object_or_404(Shop, pk=pk)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        if rating and content:
            Review.objects.create(
                shop=shop,
                user=request.user,
                rating=int(rating),
                content=content
            )
            messages.success(request, '评价发表成功！')
        else:
            messages.error(request, '请填写完整信息')
    return redirect('shop_detail', pk=pk)


def taste_analysis(request):
    """判别分析：根据用户评分数据判断口味偏好并推荐"""
    user = request.user
    is_authenticated = user.is_authenticated

    # 用户评价过的店铺 ID
    reviewed_shop_ids = set()
    # 各分类的评分数据 {category_name: [ratings...]}
    category_ratings = {}
    # 用户评价总数
    user_review_count = 0
    # 用户平均评分
    user_avg_rating = 0
    # 口味标签
    taste_tags = []
    # 推荐店铺
    recommendations = []

    if is_authenticated:
        reviews = Review.objects.filter(user=user).select_related('shop__category')
        user_review_count = reviews.count()

        if user_review_count > 0:
            all_ratings = []
            for review in reviews:
                cat_name = review.shop.category.name
                if cat_name not in category_ratings:
                    category_ratings[cat_name] = []
                category_ratings[cat_name].append(review.rating)
                reviewed_shop_ids.add(review.shop_id)
                all_ratings.append(review.rating)

            user_avg_rating = round(sum(all_ratings) / len(all_ratings), 1)

            # 计算各分类平均分，排序
            cat_avg = {}
            for cat, ratings in category_ratings.items():
                cat_avg[cat] = round(sum(ratings) / len(ratings), 1)

            # 口味判别逻辑
            sorted_cats = sorted(cat_avg.items(), key=lambda x: x[1], reverse=True)

            # 生成口味标签
            if sorted_cats:
                top_cat = sorted_cats[0]
                if top_cat[1] >= 4.5:
                    taste_tags.append(f'「{top_cat[0]}」忠实爱好者')
                elif top_cat[1] >= 4.0:
                    taste_tags.append(f'偏爱「{top_cat[0]}」')
                elif top_cat[1] >= 3.0:
                    taste_tags.append(f'对「{top_cat[0]}」评价中肯')
                else:
                    taste_tags.append(f'对「{top_cat[0]}」要求较高')

            if user_avg_rating >= 4.5:
                taste_tags.append('宽容型食客 · 手下留情')
            elif user_avg_rating >= 3.5:
                taste_tags.append('理性型食客 · 客观公正')
            elif user_avg_rating >= 2.5:
                taste_tags.append('挑剔型食客 · 标准严格')
            else:
                taste_tags.append('严苛型食客 · 舌尖达人')

            # 评分波动
            if len(all_ratings) >= 3:
                import statistics
                stdev = round(statistics.stdev(all_ratings), 1)
                if stdev <= 0.8:
                    taste_tags.append('评分稳定 · 判断一致')
                elif stdev <= 1.5:
                    taste_tags.append('评分有波动 · 因店而异')
                else:
                    taste_tags.append('评分跨度大 · 区分度高')

            # 推荐逻辑：找用户偏好的分类中未评价的高分店铺
            preferred_cats = [cat for cat, avg in sorted_cats if avg >= 3.5]
            if preferred_cats:
                rec_shops = Shop.objects.filter(
                    category__name__in=preferred_cats
                ).exclude(
                    id__in=reviewed_shop_ids
                ).annotate(
                    avg_r=Avg('reviews__rating')
                ).order_by('-avg_r')[:6]
            else:
                # 如果没有明显偏好，推荐全局高分店铺
                rec_shops = Shop.objects.exclude(
                    id__in=reviewed_shop_ids
                ).annotate(
                    avg_r=Avg('reviews__rating')
                ).order_by('-avg_r')[:6]

            recommendations = rec_shops

    # 全站热门店铺（用于未登录用户或补充推荐）
    popular_shops = Shop.objects.annotate(
        avg_r=Avg('reviews__rating'),
        rev_count=Count('reviews')
    ).order_by('-avg_r')[:6]

    # 预计算各分类平均分和百分比（用于进度条）
    cat_avg_list = []
    for cat_name, ratings in category_ratings.items():
        avg = round(sum(ratings) / len(ratings), 1)
        cat_avg_list.append({
            'name': cat_name,
            'avg': avg,
            'count': len(ratings),
            'percent': int(avg / 5 * 100),
        })
    cat_avg_list.sort(key=lambda x: x['avg'], reverse=True)

    context = {
        'is_authenticated': is_authenticated,
        'user_review_count': user_review_count,
        'user_avg_rating': user_avg_rating,
        'cat_avg_list': cat_avg_list,
        'taste_tags': taste_tags,
        'recommendations': recommendations,
        'popular_shops': popular_shops,
    }
    return render(request, 'food/taste_analysis.html', context)


def analytics(request):
    """数据可视化页面"""
    # 1. 评分分布直方图数据：1-5 星各有多少条评价
    rating_dist = [0] * 5
    for row in Review.objects.values('rating').annotate(count=Count('id')):
        if 1 <= row['rating'] <= 5:
            rating_dist[row['rating'] - 1] = row['count']

    # 2. 饼图数据：各分类店铺数量占比
    pie_rows = Shop.objects.values('category__name').annotate(count=Count('id')).order_by('-count')
    pie_labels = [r['category__name'] for r in pie_rows]
    pie_data = [r['count'] for r in pie_rows]

    context = {
        'rating_labels': json.dumps(['1星', '2星', '3星', '4星', '5星']),
        'rating_data': json.dumps(rating_dist),
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'total_reviews': Review.objects.count(),
        'total_shops': Shop.objects.count(),
        'total_categories': Category.objects.count(),
    }
    return render(request, 'food/analytics.html', context)
