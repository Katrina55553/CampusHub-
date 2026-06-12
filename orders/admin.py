from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'publisher', 'helper', 'location', 'reward', 'status', 'created_at']
    list_filter = ['status', 'location']
    search_fields = ['title', 'description']
