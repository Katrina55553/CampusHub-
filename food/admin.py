from django.contrib import admin
from .models import Category, Shop, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'avg_price', 'avg_rating', 'review_count', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'description']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['shop', 'user', 'rating', 'created_at']
    list_filter = ['rating']
