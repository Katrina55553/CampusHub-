"""口味分析与推荐服务：将 taste_analysis 视图的算法逻辑集中到这里。"""

import statistics

from django.db.models import Avg, Count

from ..models import Review, Shop


class TasteProfile:
    """基于用户评价数据构建的口味画像。"""

    def __init__(self, user):
        self.user = user
        self.review_count = 0
        self.avg_rating = 0.0
        self.category_ratings = {}
        self.category_averages = {}
        self.reviewed_shop_ids = set()
        self.taste_tags = []
        self._build()

    def _build(self):
        if not self.user or not getattr(self.user, 'is_authenticated', False):
            return

        reviews = Review.objects.filter(user=self.user).select_related('shop__category')
        self.review_count = len(reviews)
        if self.review_count == 0:
            return

        all_ratings = []
        for review in reviews:
            cat_name = review.shop.category.name
            self.category_ratings.setdefault(cat_name, []).append(review.rating)
            self.reviewed_shop_ids.add(review.shop_id)
            all_ratings.append(review.rating)

        self.avg_rating = round(sum(all_ratings) / len(all_ratings), 1)
        self.category_averages = {
            cat: round(sum(ratings) / len(ratings), 1)
            for cat, ratings in self.category_ratings.items()
        }
        self.taste_tags = self._generate_tags(all_ratings)

    def _generate_tags(self, all_ratings):
        tags = []
        sorted_cats = sorted(self.category_averages.items(), key=lambda x: x[1], reverse=True)

        if sorted_cats:
            top_cat, top_avg = sorted_cats[0]
            if top_avg >= 4.5:
                tags.append(f'「{top_cat}」忠实爱好者')
            elif top_avg >= 4.0:
                tags.append(f'偏爱「{top_cat}」')
            elif top_avg >= 3.0:
                tags.append(f'对「{top_cat}」评价中肯')
            else:
                tags.append(f'对「{top_cat}」要求较高')

        if self.avg_rating >= 4.5:
            tags.append('宽容型食客 · 手下留情')
        elif self.avg_rating >= 3.5:
            tags.append('理性型食客 · 客观公正')
        elif self.avg_rating >= 2.5:
            tags.append('挑剔型食客 · 标准严格')
        else:
            tags.append('严苛型食客 · 舌尖达人')

        if len(all_ratings) >= 3:
            stdev = round(statistics.stdev(all_ratings), 1)
            if stdev <= 0.8:
                tags.append('评分稳定 · 判断一致')
            elif stdev <= 1.5:
                tags.append('评分有波动 · 因店而异')
            else:
                tags.append('评分跨度大 · 区分度高')

        return tags

    def category_avg_list(self):
        """用于进度条展示的分类评分列表。"""
        result = []
        for cat_name, ratings in self.category_ratings.items():
            avg = round(sum(ratings) / len(ratings), 1)
            result.append({
                'name': cat_name,
                'avg': avg,
                'count': len(ratings),
                'percent': int(avg / 5 * 100),
            })
        result.sort(key=lambda x: x['avg'], reverse=True)
        return result

    def recommend(self, limit=6):
        """在用户偏好的分类中，推荐其未评价的高分店铺。"""
        if self.review_count == 0:
            return Shop.objects.none()

        preferred_cats = [
            cat for cat, avg in self.category_averages.items() if avg >= 3.5
        ]
        qs = (
            Shop.objects.exclude(id__in=self.reviewed_shop_ids)
            .annotate(avg_r=Avg('reviews__rating'))
        )
        if preferred_cats:
            qs = qs.filter(category__name__in=preferred_cats)
        return qs.order_by('-avg_r')[:limit]


def popular_shops(limit=6):
    """全站热门店铺（用于未登录用户或补充推荐）。"""
    return (
        Shop.objects.annotate(avg_r=Avg('reviews__rating'), rev_count=Count('reviews'))
        .order_by('-avg_r')[:limit]
    )
