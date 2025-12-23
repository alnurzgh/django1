# listings/api_urls.py
"""
URL маршруты для API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ListingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')

urlpatterns = [
    path('', include(router.urls)),
]


