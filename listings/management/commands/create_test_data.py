# listings/management/commands/create_test_data.py
"""
Management команда для создания тестовых данных

Использование:
    python manage.py create_test_data
    python manage.py create_test_data --with-photo  # Создать с placeholder фото
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing
# Временно отключено
# from listings.models import Listing, Amenity, ListingAmenity
from decimal import Decimal


class Command(BaseCommand):
    help = 'Создает тестовые данные: пользователя, удобства, объект жилья'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-photo',
            action='store_true',
            help='Создать объект с placeholder фото (требует наличия файла)',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='test_owner',
            help='Имя пользователя для владельца (по умолчанию: test_owner)',
        )
        parser.add_argument(
            '--email',
            type=str,
            default='owner@example.com',
            help='Email владельца',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='testpass123',
            help='Пароль владельца',
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        with_photo = options['with_photo']

        self.stdout.write('Создание тестовых данных...\n')

        # 1. Создаем или получаем пользователя
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Тестовый',
                'last_name': 'Владелец',
            }
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Создан пользователь: {username} (пароль: {password})'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠ Пользователь {username} уже существует'))

        # 2. Создаем удобства (временно отключено)
        created_amenities = []
        # amenities_data = [...]
        # for amenity_data in amenities_data:
        #     amenity, created = Amenity.objects.get_or_create(...)

        # 3. Создаем объект жилья
        listing_data = {
            'owner': user,
            'title': 'Уютная квартира в центре Алматы',
            'description': '''Просторная и светлая двухкомнатная квартира в самом центре города. 
Идеально подходит для деловой поездки или отдыха.

Особенности:
- Полностью оборудованная кухня
- Быстрый Wi-Fi
- Рядом метро и основные достопримечательности
- Кондиционер во всех комнатах
- Бесплатная парковка

Заезд с 14:00, выезд до 12:00.''',
            'address': 'ул. Абая, 150',
            'city': 'Алматы',
            'latitude': Decimal('43.238949'),
            'longitude': Decimal('76.889709'),
            'property_type': 'apartment',
            'bedrooms': 2,
            'beds': 2,
            'bathrooms': Decimal('1.0'),
            'sqft': 65,
            'max_guests': 4,
            'base_price': Decimal('12000.00'),
            'weekend_price': Decimal('15000.00'),
            'weekly_discount': 10,
            'monthly_discount': 25,
            'booking_type': 'instant',
            'min_nights': 1,
            'max_nights': 30,
            'house_rules': '''Правила дома:
- Запрещено курение
- Не шуметь после 22:00
- Запрещены домашние животные
- Уважайте соседей''',
            'is_published': True,
            'is_verified': True,
            'moderation_status': 'approved',
        }

        # Проверяем, есть ли уже такой объект
        existing_listing = Listing.objects.filter(
            owner=user,
            title=listing_data['title']
        ).first()

        if existing_listing:
            self.stdout.write(self.style.WARNING(f'⚠ Объект "{listing_data["title"]}" уже существует'))
            listing = existing_listing
        else:
            # Создаем объект
            if with_photo:
                # Пытаемся использовать placeholder фото
                # Пользователь должен сам загрузить фото через админку или API
                listing_data['photo_main'] = None
                listing = Listing.objects.create(**listing_data)
                self.stdout.write(self.style.WARNING('⚠ Фото нужно добавить вручную через админку'))
            else:
                # Создаем без фото (фото можно добавить позже)
                listing_data['photo_main'] = None
                listing = Listing.objects.create(**listing_data)
                self.stdout.write(self.style.SUCCESS(f'✓ Создан объект: {listing.title}'))
                self.stdout.write(self.style.WARNING('   ⚠ Фото не добавлено. Добавьте фото через админку или API.'))

        # 4. Добавляем удобства к объекту (временно отключено)
        # amenities_to_add = ['Wi-Fi', 'Парковка', 'Кондиционер', 'Кухня', 'Стиральная машина', 'Телевизор']
        # ...

        # Итоговая информация
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Тестовые данные созданы успешно!'))
        self.stdout.write('='*50)
        self.stdout.write(f'\nОбъект ID: {listing.id}')
        self.stdout.write(f'Владелец: {user.username} ({user.email})')
        self.stdout.write(f'Пароль: {password}')
        self.stdout.write(f'\nДля добавления фото:')
        self.stdout.write(f'1. Через админку: http://localhost:8000/admin/listings/listing/{listing.id}/change/')
        self.stdout.write(f'2. Через API: PUT /api/listings/{listing.id}/ (с токеном авторизации)')
        self.stdout.write(f'\nДля входа в админку:')
        self.stdout.write(f'URL: http://localhost:8000/admin/')
        self.stdout.write(f'Логин: {username}')
        self.stdout.write(f'Пароль: {password}')
        self.stdout.write('\n')


