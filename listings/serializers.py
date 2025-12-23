# listings/serializers.py
"""
Serializers для Django REST Framework
"""
from datetime import date
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Listing, Amenity, ListingAmenity, Availability, Booking, Review, Message, ICalSync
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class AmenitySerializer(serializers.ModelSerializer):
    """Serializer для удобств"""
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class ListingAmenitySerializer(serializers.ModelSerializer):
    """Serializer для связи Listing-Amenity"""
    amenity = AmenitySerializer(read_only=True)
    amenity_id = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), source='amenity', write_only=True
    )
    
    class Meta:
        model = ListingAmenity
        fields = ['id', 'amenity', 'amenity_id']


class ListingSerializer(serializers.ModelSerializer):
    """Serializer для объектов жилья"""
    owner = UserSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(), many=True, write_only=True, required=False
    )
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'title', 'description', 'address', 'city',
            'latitude', 'longitude', 'property_type', 'bedrooms', 'beds',
            'bathrooms', 'sqft', 'max_guests', 'base_price', 'weekend_price',
            'weekly_discount', 'monthly_discount', 'photo_main', 'is_verified',
            'is_published', 'moderation_status', 'booking_type', 'house_rules',
            'check_in_time', 'check_out_time', 'min_nights', 'max_nights',
            'list_date', 'updated_at', 'amenities', 'amenity_ids',
            'average_rating', 'review_count'
        ]
        read_only_fields = ['owner', 'is_verified', 'verification_date', 
                          'moderation_status', 'moderation_notes', 'list_date', 'updated_at']
    
    def get_average_rating(self, obj):
        """Средний рейтинг объекта"""
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None
    
    def get_review_count(self, obj):
        """Количество отзывов"""
        return obj.reviews.count()
    
    def create(self, validated_data):
        """Создание объекта с удобствами"""
        amenity_ids = validated_data.pop('amenity_ids', [])
        listing = Listing.objects.create(**validated_data)
        
        for amenity in amenity_ids:
            ListingAmenity.objects.create(listing=listing, amenity=amenity)
        
        return listing
    
    def update(self, instance, validated_data):
        """Обновление объекта с удобствами"""
        amenity_ids = validated_data.pop('amenity_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if amenity_ids is not None:
            # Обновляем удобства
            instance.amenities.all().delete()
            for amenity in amenity_ids:
                ListingAmenity.objects.create(listing=instance, amenity=amenity)
        
        return instance


class ListingListSerializer(serializers.ModelSerializer):
    """Упрощенный serializer для списка объектов (быстрый поиск)"""
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'address', 'city', 'property_type',
            'bedrooms', 'beds', 'bathrooms', 'sqft', 'base_price',
            'photo_main', 'is_verified', 'average_rating'
        ]
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return None


class AvailabilitySerializer(serializers.ModelSerializer):
    """Serializer для календаря доступности"""
    class Meta:
        model = Availability
        fields = ['id', 'listing', 'date', 'is_available', 'price_override', 
                 'notes', 'source', 'external_id']
        read_only_fields = ['source', 'external_id']


class BookingSerializer(serializers.ModelSerializer):
    """Serializer для бронирований"""
    guest = UserSerializer(read_only=True)
    listing = ListingListSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_published=True), 
        source='listing', 
        write_only=True
    )
    nights = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_id', 'guest', 'check_in', 'check_out',
            'guests_count', 'total_price', 'status', 'owner_response',
            'payment_status', 'payment_date', 'special_requests',
            'created_at', 'nights'
        ]
        read_only_fields = ['guest', 'total_price', 'status', 'owner_response',
                          'owner_response_at', 'payment_status', 'payment_date', 
                          'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer для отзывов"""
    reviewer = UserSerializer(read_only=True)
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.filter(status='completed'),
        source='booking',
        write_only=True
    )
    
    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'booking_id', 'reviewer', 'listing', 'rating',
            'comment', 'cleanliness_rating', 'communication_rating',
            'location_rating', 'value_rating', 'is_verified', 'created_at'
        ]
        read_only_fields = ['reviewer', 'listing', 'is_verified', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Создание отзыва с автоматическим заполнением reviewer и listing"""
        booking = validated_data['booking']
        validated_data['reviewer'] = booking.guest
        validated_data['listing'] = booking.listing
        return super().create(validated_data)


class MessageSerializer(serializers.ModelSerializer):
    """Serializer для сообщений"""
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'booking', 'sender', 'recipient', 'listing', 'subject',
            'content', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['sender', 'is_read', 'read_at', 'created_at']


class ICalSyncSerializer(serializers.ModelSerializer):
    """Serializer для синхронизации iCal"""
    class Meta:
        model = ICalSync
        fields = ['id', 'listing', 'url', 'is_active', 'last_sync', 'sync_frequency']
        read_only_fields = ['last_sync']


class SearchSerializer(serializers.Serializer):
    """Serializer для параметров поиска"""
    check_in = serializers.DateField(required=True)
    check_out = serializers.DateField(required=True)
    city = serializers.CharField(required=False, allow_blank=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    property_type = serializers.ChoiceField(choices=Listing._meta.get_field('property_type').choices, required=False)
    min_bedrooms = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    min_guests = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    
    def validate(self, data):
        """Проверка дат"""
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")
        
        if data['check_in'] < date.today():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом")
        
        return data
