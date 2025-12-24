# listings/services.py
# Упрощенная версия - только основные функции без несуществующих моделей
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional
from .models import Listing


class AvailabilityService:
    """Сервис для проверки доступности объектов (упрощенная версия)"""
    
    @staticmethod
    def is_available(listing: Listing, check_in: date, check_out: date) -> bool:
        """Проверяет, доступен ли объект на указанный период."""
        nights = (check_out - check_in).days
        if listing.min_nights and nights < listing.min_nights:
            return False
        if listing.max_nights and nights > listing.max_nights:
            return False
        return True
    
    @staticmethod
    def get_available_listings(check_in: date, check_out: date, city: Optional[str] = None, 
                               max_price: Optional[Decimal] = None, 
                               property_type: Optional[str] = None,
                               min_bedrooms: Optional[int] = None,
                               min_guests: Optional[int] = None) -> List[Listing]:
        """Получает список доступных объектов с фильтрами."""
        nights = (check_out - check_in).days
        
        queryset = Listing.objects.filter(is_published=True)
        
        if nights > 0:
            if hasattr(Listing, 'min_nights'):
                queryset = queryset.filter(min_nights__lte=nights)
            if hasattr(Listing, 'max_nights'):
                queryset = queryset.filter(max_nights__gte=nights)
        
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)
        
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)
        
        queryset = queryset.order_by('-is_verified', '-list_date')
        
        return list(queryset)


