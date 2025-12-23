# listings/serializers.py
from datetime import date
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
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
            'list_date', 'updated_at', 'average_rating', 'review_count'
        ]
        read_only_fields = ['owner', 'is_verified', 'verification_date', 
                          'moderation_status', 'moderation_notes', 'list_date', 'updated_at']
    
    def get_average_rating(self, obj):
        return None
    
    def get_review_count(self, obj):
        return 0


class ListingListSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'address', 'city', 'property_type',
            'bedrooms', 'beds', 'bathrooms', 'sqft', 'base_price',
            'photo_main', 'is_verified', 'average_rating'
        ]
    
    def get_average_rating(self, obj):
        return None


class SearchSerializer(serializers.Serializer):
    check_in = serializers.DateField(required=True)
    check_out = serializers.DateField(required=True)
    city = serializers.CharField(required=False, allow_blank=True)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    property_type = serializers.ChoiceField(choices=Listing._meta.get_field('property_type').choices, required=False)
    min_bedrooms = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    min_guests = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    
    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError("Дата выезда должна быть позже даты заезда")
        if data['check_in'] < date.today():
            raise serializers.ValidationError("Дата заезда не может быть в прошлом")
        return data
