# listings/admin.py
from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'base_price', 'is_published', 'is_verified', 'list_date')
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'is_verified', 'city', 'property_type', 'moderation_status')
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'address', 'city')
    list_per_page = 50
    readonly_fields = ('list_date', 'updated_at', 'verification_date')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'title', 'description', 'photo_main')
        }),
        ('Местоположение', {
            'fields': ('address', 'city', 'latitude', 'longitude')
        }),
        ('Характеристики', {
            'fields': ('property_type', 'bedrooms', 'beds', 'bathrooms', 'sqft', 'max_guests')
        }),
        ('Цены', {
            'fields': ('base_price', 'weekend_price', 'weekly_discount', 'monthly_discount')
        }),
        ('Бронирование', {
            'fields': ('booking_type', 'min_nights', 'max_nights', 'check_in_time', 'check_out_time', 'house_rules')
        }),
        ('Статус', {
            'fields': ('is_published', 'is_verified', 'verification_date', 'moderation_status', 'moderation_notes')
        }),
        ('Даты', {
            'fields': ('list_date', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs
