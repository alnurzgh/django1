# listings/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

class Listing(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name="Владелец", null=True, blank=True)
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание", blank=True)
    
    address = models.CharField("Адрес", max_length=200)
    city = models.CharField("Город", max_length=100)
    latitude = models.DecimalField("Широта", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("Долгота", max_digits=9, decimal_places=6, null=True, blank=True)
    
    property_type = models.CharField("Тип недвижимости", max_length=50, choices=[
        ('apartment', 'Квартира'), ('house', 'Дом'), ('room', 'Комната'),
        ('studio', 'Студия'), ('villa', 'Вилла'),
    ], default='apartment', null=True, blank=True)
    bedrooms = models.IntegerField("Кол-во спален", default=1)
    beds = models.IntegerField("Кол-во кроватей", default=1, null=True, blank=True)
    bathrooms = models.DecimalField("Кол-во ванных", max_digits=3, decimal_places=1, default=1.0, null=True, blank=True)
    sqft = models.IntegerField("Площадь (кв.м)")
    max_guests = models.IntegerField("Макс. гостей", default=2, null=True, blank=True)
    
    base_price = models.DecimalField("Базовая цена за ночь", max_digits=10, decimal_places=2, default=Decimal('0.00'))
    weekend_price = models.DecimalField("Цена на выходные", max_digits=10, decimal_places=2, null=True, blank=True)
    weekly_discount = models.IntegerField("Скидка за неделю (%)", default=0, null=True, blank=True)
    monthly_discount = models.IntegerField("Скидка за месяц (%)", default=0, null=True, blank=True)
    
    photo_main = models.ImageField("Главное фото", upload_to='photos/%Y/%m/%d/', blank=True, null=True)
    
    is_verified = models.BooleanField("Проверено", default=False, null=True, blank=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    verification_date = models.DateTimeField("Дата верификации", null=True, blank=True)
    moderation_status = models.CharField("Статус модерации", max_length=20, choices=[
        ('pending', 'На модерации'), ('approved', 'Одобрено'), ('rejected', 'Отклонено'),
    ], default='pending', null=True, blank=True)
    moderation_notes = models.TextField("Заметки модератора", blank=True, null=True)
    
    booking_type = models.CharField("Тип бронирования", max_length=20, choices=[
        ('instant', 'Мгновенное бронирование'), ('request', 'По запросу'),
    ], default='request', null=True, blank=True)
    
    house_rules = models.TextField("Правила дома", blank=True, null=True)
    check_in_time = models.TimeField("Время заезда", default='14:00', null=True, blank=True)
    check_out_time = models.TimeField("Время выезда", default='12:00', null=True, blank=True)
    
    min_nights = models.IntegerField("Мин. ночей", default=1, null=True, blank=True)
    max_nights = models.IntegerField("Макс. ночей", default=365, null=True, blank=True)
    
    list_date = models.DateTimeField("Дата создания", default=timezone.now, blank=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-is_verified', '-list_date']