# listings/api_views.py
"""
API Views для Django REST Framework
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from datetime import date

from .models import (
    Listing, Amenity, Availability, Booking, Review, Message, ICalSync
)
from .serializers import (
    ListingSerializer, ListingListSerializer, AmenitySerializer,
    AvailabilitySerializer, BookingSerializer, ReviewSerializer,
    MessageSerializer, ICalSyncSerializer, SearchSerializer
)
from .services import AvailabilityService, BookingService, ICalSyncService


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для объектов жилья
    
    list: Список всех опубликованных объектов (с фильтрацией)
    retrieve: Детальная информация об объекте
    create: Создание нового объекта (требует авторизации)
    update: Обновление объекта (только владелец)
    """
    queryset = Listing.objects.filter(is_published=True)
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'address', 'city']
    ordering_fields = ['list_date', 'base_price', 'is_verified']
    ordering = ['-is_verified', '-list_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ListingListSerializer
        return ListingSerializer
    
    def get_permissions(self):
        """Разрешения для разных действий"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def get_queryset(self):
        """Фильтрация объектов"""
        queryset = super().get_queryset()
        
        # Фильтры из query параметров
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        property_type = self.request.query_params.get('property_type', None)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        
        max_price = self.request.query_params.get('max_price', None)
        if max_price:
            queryset = queryset.filter(base_price__lte=max_price)
        
        min_bedrooms = self.request.query_params.get('min_bedrooms', None)
        if min_bedrooms:
            queryset = queryset.filter(bedrooms__gte=min_bedrooms)
        
        min_guests = self.request.query_params.get('min_guests', None)
        if min_guests:
            queryset = queryset.filter(max_guests__gte=min_guests)
        
        # Поиск по доступности на даты
        check_in = self.request.query_params.get('check_in', None)
        check_out = self.request.query_params.get('check_out', None)
        if check_in and check_out:
            try:
                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                
                # Используем сервис для фильтрации по доступности
                from decimal import Decimal
                listings_list = AvailabilityService.get_available_listings(
                    check_in_date, check_out_date,
                    city=city,
                    max_price=Decimal(max_price) if max_price else None,
                    property_type=property_type,
                    min_bedrooms=int(min_bedrooms) if min_bedrooms else None,
                    min_guests=int(min_guests) if min_guests else None
                )
                # Преобразуем список обратно в QuerySet для пагинации
                listing_ids = [l.id for l in listings_list]
                queryset = Listing.objects.filter(id__in=listing_ids, is_published=True)
            except ValueError:
                pass  # Невалидные даты, игнорируем фильтр
        
        return queryset
    
    def perform_create(self, serializer):
        """При создании объекта устанавливаем владельца"""
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """
        Получить доступность объекта на конкретные даты
        
        Параметры: ?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD
        """
        listing = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')
        
        if not check_in or not check_out:
            return Response(
                {'error': 'Требуются параметры check_in и check_out'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = date.fromisoformat(check_in)
            check_out_date = date.fromisoformat(check_out)
            
            is_available = AvailabilityService.is_available(listing, check_in_date, check_out_date)
            total_price = listing.calculate_total_price(check_in_date, check_out_date) if is_available else None
            
            return Response({
                'available': is_available,
                'total_price': float(total_price) if total_price else None,
                'nights': (check_out_date - check_in_date).days
            })
        except ValueError:
            return Response(
                {'error': 'Неверный формат даты. Используйте YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        Поиск объектов с фильтрами по доступности
        
        POST /api/listings/search/
        Body: {
            "check_in": "2024-06-01",
            "check_out": "2024-06-10",
            "city": "Алматы",
            "max_price": 10000,
            ...
        }
        """
        serializer = SearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        listings = AvailabilityService.get_available_listings(
            check_in=data['check_in'],
            check_out=data['check_out'],
            city=data.get('city'),
            max_price=data.get('max_price'),
            property_type=data.get('property_type'),
            min_bedrooms=data.get('min_bedrooms'),
            min_guests=data.get('min_guests')
        )
        
        serializer_response = ListingListSerializer(listings, many=True, context={'request': request})
        return Response(serializer_response.data)


class AmenityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для удобств (только чтение)"""
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [AllowAny]


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet для бронирований"""
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Пользователь видит только свои бронирования или бронирования своих объектов"""
        user = self.request.user
        return Booking.objects.filter(
            Q(guest=user) | Q(listing__owner=user)
        ).distinct()
    
    def create(self, request, *args, **kwargs):
        """Создание бронирования с проверкой доступности"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        listing_id = serializer.validated_data.get('listing').id
        listing = Listing.objects.get(id=listing_id)
        check_in = serializer.validated_data.get('check_in')
        check_out = serializer.validated_data.get('check_out')
        guests_count = serializer.validated_data.get('guests_count')
        special_requests = serializer.validated_data.get('special_requests', '')
        
        # Используем BookingService для создания с проверкой доступности
        booking, error_message = BookingService.create_booking(
            listing=listing,
            guest=request.user,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            special_requests=special_requests
        )
        
        if booking:
            serializer = self.get_serializer(booking)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Подтвердить бронирование (владелец)"""
        booking = self.get_object()
        success, message = BookingService.confirm_booking(booking, request.user)
        
        if success:
            serializer = self.get_serializer(booking)
            return Response(serializer.data)
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Отклонить бронирование (владелец)"""
        booking = self.get_object()
        reason = request.data.get('reason', '')
        success, message = BookingService.reject_booking(booking, request.user, reason)
        
        if success:
            serializer = self.get_serializer(booking)
            return Response(serializer.data)
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Мои бронирования как гостя"""
        bookings = Booking.objects.filter(guest=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_listings_bookings(self, request):
        """Бронирования моих объектов (как владельца)"""
        bookings = Booking.objects.filter(listing__owner=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов"""
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Отзывы на объекты или конкретного объекта"""
        listing_id = self.request.query_params.get('listing', None)
        queryset = Review.objects.filter(is_verified=True)
        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset
    
    def perform_create(self, serializer):
        """При создании устанавливаем автора"""
        serializer.save(reviewer=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet для сообщений"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Сообщения текущего пользователя"""
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        """При создании устанавливаем отправителя"""
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Пометить сообщение как прочитанное"""
        message = self.get_object()
        if message.recipient == request.user:
            message.is_read = True
            from django.utils import timezone
            message.read_at = timezone.now()
            message.save()
            return Response({'status': 'marked as read'})
        return Response(
            {'error': 'Вы не получатель этого сообщения'},
            status=status.HTTP_403_FORBIDDEN
        )


class ICalSyncViewSet(viewsets.ModelViewSet):
    """ViewSet для синхронизации iCal"""
    serializer_class = ICalSyncSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Только iCal синхронизации для объектов текущего пользователя"""
        return ICalSync.objects.filter(listing__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Синхронизировать iCal календарь"""
        ical_sync = self.get_object()
        success, message = ICalSyncService.sync_ical(ical_sync)
        
        if success:
            serializer = self.get_serializer(ical_sync)
            return Response({
                'status': 'success',
                'message': message,
                'data': serializer.data
            })
        return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
