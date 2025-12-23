# listings/services.py
"""
Сервисы для проверки доступности, синхронизации календарей и бизнес-логики
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Tuple, Optional
from django.db.models import Q
from django.utils import timezone
from .models import Listing, Availability, Booking, ICalSync
import requests
from icalendar import Calendar
import logging

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Сервис для проверки доступности объектов"""
    
    @staticmethod
    def is_available(listing: Listing, check_in: date, check_out: date) -> bool:
        """
        Проверяет, доступен ли объект на указанный период.
        
        Args:
            listing: Объект Listing
            check_in: Дата заезда
            check_out: Дата выезда
        
        Returns:
            True если доступен, False если занят
        """
        # Проверяем минимальные и максимальные периоды
        nights = (check_out - check_in).days
        if nights < listing.min_nights or nights > listing.max_nights:
            return False
        
        # Проверяем активные бронирования
        overlapping_bookings = Booking.objects.filter(
            listing=listing,
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=['confirmed', 'pending']
        ).exists()
        
        if overlapping_bookings:
            return False
        
        # Проверяем календарь доступности
        unavailable_dates = Availability.objects.filter(
            listing=listing,
            date__gte=check_in,
            date__lt=check_out,
            is_available=False
        ).exists()
        
        if unavailable_dates:
            return False
        
        # Проверяем, что все даты в календаре доступны или не указаны
        # Если есть хотя бы одна недоступная дата в периоде - период недоступен
        date_range = AvailabilityService._get_date_range(check_in, check_out)
        for check_date in date_range:
            availability = Availability.objects.filter(
                listing=listing,
                date=check_date
            ).first()
            
            if availability and not availability.is_available:
                return False
        
        return True
    
    @staticmethod
    def get_available_listings(check_in: date, check_out: date, city: Optional[str] = None, 
                               max_price: Optional[Decimal] = None, 
                               property_type: Optional[str] = None,
                               min_bedrooms: Optional[int] = None,
                               min_guests: Optional[int] = None) -> List[Listing]:
        """
        Получает список доступных объектов с фильтрами.
        Оптимизированный QuerySet для поиска по доступности.
        
        Args:
            check_in: Дата заезда
            check_out: Дата выезда
            city: Фильтр по городу
            max_price: Максимальная цена за ночь
            property_type: Тип недвижимости
            min_bedrooms: Минимальное количество спален
            min_guests: Минимальное количество гостей
        
        Returns:
            QuerySet доступных объектов
        """
        nights = (check_out - check_in).days
        
        # Базовый QuerySet с фильтрами
        queryset = Listing.objects.filter(
            is_published=True,
            min_nights__lte=nights,
            max_nights__gte=nights
        )
        
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
        
        # Исключаем объекты с пересекающимися бронированиями
        booked_listing_ids = Booking.objects.filter(
            check_in__lt=check_out,
            check_out__gt=check_in,
            status__in=['confirmed', 'pending']
        ).values_list('listing_id', flat=True).distinct()
        
        queryset = queryset.exclude(id__in=booked_listing_ids)
        
        # Исключаем объекты с недоступными датами в календаре
        unavailable_listing_ids = Availability.objects.filter(
            date__gte=check_in,
            date__lt=check_out,
            is_available=False
        ).values_list('listing_id', flat=True).distinct()
        
        queryset = queryset.exclude(id__in=unavailable_listing_ids)
        
        # Сортируем: сначала верифицированные, потом по дате создания
        queryset = queryset.order_by('-is_verified', '-list_date')
        
        # Дополнительная проверка доступности для каждого объекта
        # (на случай если есть частично заполненный календарь)
        available_listings = []
        for listing in queryset:
            if AvailabilityService.is_available(listing, check_in, check_out):
                available_listings.append(listing)
        
        return available_listings
    
    @staticmethod
    def mark_dates_unavailable(listing: Listing, start_date: date, end_date: date, 
                               source: str = 'manual', external_id: str = ''):
        """
        Помечает диапазон дат как недоступный в календаре.
        
        Args:
            listing: Объект Listing
            start_date: Начальная дата
            end_date: Конечная дата (не включая)
            source: Источник блокировки ('manual', 'ical', 'booking')
            external_id: Внешний ID для синхронизации
        """
        date_range = AvailabilityService._get_date_range(start_date, end_date)
        
        for check_date in date_range:
            Availability.objects.update_or_create(
                listing=listing,
                date=check_date,
                defaults={
                    'is_available': False,
                    'source': source,
                    'external_id': external_id
                }
            )
    
    @staticmethod
    def mark_dates_available(listing: Listing, start_date: date, end_date: date):
        """
        Помечает диапазон дат как доступный в календаре.
        
        Args:
            listing: Объект Listing
            start_date: Начальная дата
            end_date: Конечная дата (не включая)
        """
        date_range = AvailabilityService._get_date_range(start_date, end_date)
        
        for check_date in date_range:
            Availability.objects.update_or_create(
                listing=listing,
                date=check_date,
                defaults={
                    'is_available': True,
                    'source': 'manual'
                }
            )
    
    @staticmethod
    def _get_date_range(start_date: date, end_date: date) -> List[date]:
        """Генерирует список дат в диапазоне"""
        date_list = []
        current_date = start_date
        while current_date < end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        return date_list


class ICalSyncService:
    """Сервис для синхронизации с внешними iCal календарями"""
    
    @staticmethod
    def sync_ical(ical_sync: ICalSync) -> Tuple[bool, str]:
        """
        Синхронизирует календарь объекта с внешним iCal календарем.
        
        Args:
            ical_sync: Объект ICalSync
        
        Returns:
            Tuple (success: bool, message: str)
        """
        try:
            # Загружаем iCal календарь
            response = requests.get(ical_sync.url, timeout=10)
            response.raise_for_status()
            
            # Парсим календарь
            calendar = Calendar.from_ical(response.content)
            
            # Очищаем старые записи из этого источника для этого объекта
            Availability.objects.filter(
                listing=ical_sync.listing,
                source='ical',
                external_id__startswith=f"ical_{ical_sync.id}_"
            ).delete()
            
            blocked_dates = 0
            
            # Обрабатываем события в календаре
            for component in calendar.walk('vevent'):
                # Получаем даты начала и конца события
                dtstart = component.get('dtstart')
                dtend = component.get('dtend')
                
                if not dtstart or not dtend:
                    continue
                
                # Преобразуем в date объекты
                start_date = dtstart.dt
                end_date = dtend.dt
                
                if isinstance(start_date, datetime):
                    start_date = start_date.date()
                if isinstance(end_date, datetime):
                    end_date = end_date.date()
                
                # Получаем уникальный ID события
                uid = str(component.get('uid', ''))
                external_id = f"ical_{ical_sync.id}_{uid}"
                
                # Помечаем даты как недоступные
                AvailabilityService.mark_dates_unavailable(
                    ical_sync.listing,
                    start_date,
                    end_date,
                    source='ical',
                    external_id=external_id
                )
                
                blocked_dates += (end_date - start_date).days
            
            # Обновляем время последней синхронизации
            ical_sync.last_sync = timezone.now()
            ical_sync.save(update_fields=['last_sync'])
            
            return True, f"Синхронизировано. Заблокировано {blocked_dates} дней"
            
        except requests.RequestException as e:
            logger.error(f"Ошибка загрузки iCal: {e}")
            return False, f"Ошибка загрузки календаря: {str(e)}"
        except Exception as e:
            logger.error(f"Ошибка синхронизации iCal: {e}")
            return False, f"Ошибка синхронизации: {str(e)}"
    
    @staticmethod
    def sync_all_active():
        """Синхронизирует все активные iCal календари"""
        active_syncs = ICalSync.objects.filter(is_active=True)
        results = []
        
        for ical_sync in active_syncs:
            success, message = ICalSyncService.sync_ical(ical_sync)
            results.append({
                'listing': ical_sync.listing.title,
                'success': success,
                'message': message
            })
        
        return results


class BookingService:
    """Сервис для работы с бронированиями"""
    
    @staticmethod
    def create_booking(listing: Listing, guest, check_in: date, check_out: date, 
                      guests_count: int, special_requests: str = '') -> Tuple[Optional[Booking], str]:
        """
        Создает новое бронирование с проверкой доступности.
        
        Args:
            listing: Объект Listing
            guest: Пользователь (гость)
            check_in: Дата заезда
            check_out: Дата выезда
            guests_count: Количество гостей
            special_requests: Особые пожелания
        
        Returns:
            Tuple (Booking or None, error_message)
        """
        # Проверяем доступность
        if not AvailabilityService.is_available(listing, check_in, check_out):
            return None, "Объект недоступен на выбранные даты"
        
        # Проверяем количество гостей
        if guests_count > listing.max_guests:
            return None, f"Максимальное количество гостей: {listing.max_guests}"
        
        # Рассчитываем цену
        total_price = listing.calculate_total_price(check_in, check_out)
        
        # Определяем статус в зависимости от типа бронирования
        status = 'confirmed' if listing.booking_type == 'instant' else 'pending'
        
        # Создаем бронирование
        booking = Booking.objects.create(
            listing=listing,
            guest=guest,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            total_price=total_price,
            status=status,
            special_requests=special_requests
        )
        
        # Если мгновенное бронирование, блокируем даты
        if status == 'confirmed':
            AvailabilityService.mark_dates_unavailable(
                listing, check_in, check_out, source='booking', 
                external_id=f"booking_{booking.id}"
            )
        
        return booking, ""
    
    @staticmethod
    def confirm_booking(booking: Booking, owner) -> Tuple[bool, str]:
        """
        Подтверждает бронирование владельцем.
        
        Args:
            booking: Объект Booking
            owner: Владелец (User)
        
        Returns:
            Tuple (success: bool, message: str)
        """
        if booking.listing.owner != owner:
            return False, "Вы не владелец этого объекта"
        
        if booking.status != 'pending':
            return False, f"Бронирование уже в статусе: {booking.status}"
        
        # Проверяем доступность еще раз (на случай если объект стал занят)
        if not AvailabilityService.is_available(booking.listing, booking.check_in, booking.check_out):
            return False, "Объект больше недоступен на эти даты"
        
        booking.status = 'confirmed'
        booking.owner_response = True
        booking.owner_response_at = timezone.now()
        booking.save()
        
        # Блокируем даты в календаре
        AvailabilityService.mark_dates_unavailable(
            booking.listing, booking.check_in, booking.check_out, 
            source='booking', external_id=f"booking_{booking.id}"
        )
        
        return True, "Бронирование подтверждено"
    
    @staticmethod
    def reject_booking(booking: Booking, owner, reason: str = '') -> Tuple[bool, str]:
        """
        Отклоняет бронирование владельцем.
        
        Args:
            booking: Объект Booking
            owner: Владелец (User)
            reason: Причина отклонения
        
        Returns:
            Tuple (success: bool, message: str)
        """
        if booking.listing.owner != owner:
            return False, "Вы не владелец этого объекта"
        
        if booking.status != 'pending':
            return False, f"Бронирование уже в статусе: {booking.status}"
        
        booking.status = 'cancelled'
        booking.owner_response = False
        booking.owner_response_at = timezone.now()
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = reason
        booking.save()
        
        return True, "Бронирование отклонено"


