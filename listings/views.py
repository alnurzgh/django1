# listings/views.py
from django.shortcuts import render, get_object_or_404
from .models import Listing

def index(request):
    # Получаем все опубликованные объявления, сортируем по дате
    listings = Listing.objects.filter(is_published=True).order_by('-list_date')
    
    context = {
        'listings': listings
    }
    return render(request, 'listings/listings.html', context)

def listing(request, listing_id):
    # Получаем конкретное объявление или ошибку 404
    listing = get_object_or_404(Listing, pk=listing_id)
    
    context = {
        'listing': listing
    }
    return render(request, 'listings/listing.html', context)