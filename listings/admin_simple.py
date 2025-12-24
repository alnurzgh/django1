# listings/admin.py - упрощенная версия
from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'price', 'is_published', 'list_date')
    list_display_links = ('id', 'title')
    list_filter = ('is_published',)
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'address', 'city')
    list_per_page = 25



