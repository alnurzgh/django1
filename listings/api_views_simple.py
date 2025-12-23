# listings/api_views.py
# Временная упрощенная версия - только ListingViewSet
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from datetime import date

from .models import Listing
from .serializers import (
    ListingSerializer, ListingListSerializer, SearchSerializer
)
from .services import AvailabilityService


class ListingViewSet(viewsets.ModelViewSet):
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
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        
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
        
        check_in = self.request.query_params.get('check_in', None)
        check_out = self.request.query_params.get('check_out', None)
        if check_in and check_out:
            try:
                check_in_date = date.fromisoformat(check_in)
                check_out_date = date.fromisoformat(check_out)
                
                from decimal import Decimal
                listings_list = AvailabilityService.get_available_listings(
                    check_in_date, check_out_date,
                    city=city,
                    max_price=Decimal(max_price) if max_price else None,
                    property_type=property_type,
                    min_bedrooms=int(min_bedrooms) if min_bedrooms else None,
                    min_guests=int(min_guests) if min_guests else None
                )
                listing_ids = [l.id for l in listings_list]
                queryset = Listing.objects.filter(id__in=listing_ids, is_published=True)
            except ValueError:
                pass
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
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

