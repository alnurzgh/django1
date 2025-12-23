# listings/api_urls.py
"""
URL маршруты для API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ListingViewSet, AmenityViewSet, BookingViewSet,
    ReviewViewSet, MessageViewSet, ICalSyncViewSet
)

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'amenities', AmenityViewSet, basename='amenity')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'ical-syncs', ICalSyncViewSet, basename='icalsync')

urlpatterns = [
    path('', include(router.urls)),
]


