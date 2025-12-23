# listings/management/commands/create_listings_from_images.py
"""
Management команда для создания объявлений из папок с фотографиями

Использование:
    python manage.py create_listings_from_images
    python manage.py create_listings_from_images --path img
"""
import os
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files import File
from django.contrib.auth.models import User
from django.conf import settings
from listings.models import Listing
# Временно отключено
# from listings.models import Listing, Amenity, ListingAmenity
# Amenity = None
# ListingAmenity = None
from decimal import Decimal
from django.utils import timezone


class Command(BaseCommand):
    help = 'Создает объявления из папок с фотографиями в директории img/'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='img',
            help='Путь к папке с изображениями (по умолчанию: img)',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='test_owner',
            help='Имя пользователя для владельца',
        )

    def handle(self, *args, **options):
        images_path = Path(options['path'])
        username = options['username']

        if not images_path.exists():
            self.stdout.write(self.style.ERROR(f'Папка {images_path} не существует!'))
            return

        # Создаем или получаем пользователя
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@example.com',
                'first_name': 'Владелец',
                'last_name': 'Недвижимости',
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Получаем или создаем удобства (временно отключено)
        # amenities_map = self._get_or_create_amenities()

        # Описания для разных типов объектов
        descriptions = {
            '1 house': '''Просторный частный дом в тихом районе Алматы. Идеально подходит для большой семьи или компании друзей, желающих провести незабываемое время вместе.

Особенности:
• Большая гостиная с камином
• Полностью оборудованная кухня
• Уютные спальни
• Частный двор с зоной отдыха
• Современная мебель и техника
• Быстрый интернет Wi-Fi

Расположен в экологически чистом районе, недалеко от основных транспортных магистралей.''',

            '2 house': '''Уютный современный дом с прекрасным видом. Отличный выбор для тех, кто ценит комфорт и уединение.

Удобства:
• Светлые просторные комнаты
• Современный ремонт
• Вся необходимая техника
• Тихий район
• Парковка на территории
• Близость к природе

Идеально для семейного отдыха или рабочей поездки.''',

            '3 house': '''Стильный дом с современным дизайном интерьера. Каждая деталь продумана для максимального комфорта гостей.

Что внутри:
• Дизайнерский интерьер
• Просторные жилые зоны
• Удобная планировка
• Современная бытовая техника
• Уютная атмосфера
• Все для комфортного проживания

Отличное место для тех, кто любит качественный отдых.''',

            '4 house': '''Комфортабельный дом для отдыха и работы. Удачное сочетание функциональности и уюта.

Преимущества:
• Удобное расположение
• Просторные комнаты
• Все удобства
• Безопасный район
• Легко добраться до центра
• Тишина и покой

Подойдет как для короткого, так и для длительного пребывания.''',

            '5 house': '''Роскошный дом премиум класса с эксклюзивным интерьером. Идеальное место для особых случаев.

Роскошь и комфорт:
• Элитная отделка
• Просторные помещения
• Премиальная мебель
• Вся необходимая техника
• Изысканный дизайн
• Максимальный комфорт

Для тех, кто ценит качество и стиль жизни.''',

            '6 house': '''Красивый семейный дом в зеленом районе. Идеален для семей с детьми и любителей спокойного отдыха.

Особенности:
• Безопасный район
• Зеленая зона рядом
• Просторный двор
• Уютные комнаты
• Все для комфорта
• Детская площадка неподалеку

Создан для комфортного семейного отдыха.'''
        }

        # Данные для каждого объекта (вариации характеристик)
        listings_config = {
            '1 house': {
                'property_type': 'house',
                'bedrooms': 4,
                'beds': 4,
                'bathrooms': Decimal('2.0'),
                'sqft': 150,
                'max_guests': 8,
                'base_price': Decimal('25000.00'),
                'city': 'Алматы',
                'address': 'ул. Сатпаева, 45',
                'latitude': Decimal('43.250000'),
                'longitude': Decimal('76.900000'),
            },
            '2 house': {
                'property_type': 'house',
                'bedrooms': 3,
                'beds': 3,
                'bathrooms': Decimal('2.0'),
                'sqft': 120,
                'max_guests': 6,
                'base_price': Decimal('20000.00'),
                'city': 'Алматы',
                'address': 'ул. Рыскулова, 120',
                'latitude': Decimal('43.240000'),
                'longitude': Decimal('76.890000'),
            },
            '3 house': {
                'property_type': 'house',
                'bedrooms': 3,
                'beds': 3,
                'bathrooms': Decimal('1.5'),
                'sqft': 110,
                'max_guests': 5,
                'base_price': Decimal('18000.00'),
                'city': 'Алматы',
                'address': 'пр. Абылай хана, 78',
                'latitude': Decimal('43.230000'),
                'longitude': Decimal('76.880000'),
            },
            '4 house': {
                'property_type': 'house',
                'bedrooms': 2,
                'beds': 2,
                'bathrooms': Decimal('1.0'),
                'sqft': 90,
                'max_guests': 4,
                'base_price': Decimal('15000.00'),
                'city': 'Алматы',
                'address': 'ул. Толе би, 95',
                'latitude': Decimal('43.220000'),
                'longitude': Decimal('76.870000'),
            },
            '5 house': {
                'property_type': 'villa',
                'bedrooms': 5,
                'beds': 5,
                'bathrooms': Decimal('3.0'),
                'sqft': 200,
                'max_guests': 10,
                'base_price': Decimal('35000.00'),
                'city': 'Алматы',
                'address': 'ул. Коктем, 15',
                'latitude': Decimal('43.260000'),
                'longitude': Decimal('76.910000'),
            },
            '6 house': {
                'property_type': 'house',
                'bedrooms': 3,
                'beds': 3,
                'bathrooms': Decimal('2.0'),
                'sqft': 130,
                'max_guests': 6,
                'base_price': Decimal('22000.00'),
                'city': 'Алматы',
                'address': 'ул. Макатаева, 60',
                'latitude': Decimal('43.235000'),
                'longitude': Decimal('76.885000'),
            },
        }

        # Обрабатываем каждую папку
        folders = sorted([d for d in images_path.iterdir() if d.is_dir() and 'house' in d.name.lower()])
        
        if not folders:
            self.stdout.write(self.style.WARNING(f'Не найдено папок с "house" в названии в {images_path}'))
            return

        created_count = 0
        skipped_count = 0

        for folder in folders:
            folder_name = folder.name
            
            # Проверяем, не существует ли уже объявление с таким названием
            title = f'Дом "{folder_name.replace(" house", "")}"'
            if Listing.objects.filter(owner=user, title__icontains=folder_name.replace(" house", "")).exists():
                self.stdout.write(self.style.WARNING(f'[!] Объявление для {folder_name} уже существует, пропускаем'))
                skipped_count += 1
                continue

            # Находим первое изображение в папке
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            images = [f for f in folder.iterdir() 
                     if f.is_file() and f.suffix.lower() in image_extensions]
            
            if not images:
                self.stdout.write(self.style.WARNING(f'[!] В папке {folder_name} нет изображений'))
                continue

            # Берем первое изображение
            source_image = images[0]
            
            # Получаем конфигурацию или используем значения по умолчанию
            config = listings_config.get(folder_name, {
                'property_type': 'house',
                'bedrooms': 2,
                'beds': 2,
                'bathrooms': Decimal('1.0'),
                'sqft': 80,
                'max_guests': 4,
                'base_price': Decimal('15000.00'),
                'city': 'Алматы',
                'address': 'ул. Примерная, 1',
                'latitude': Decimal('43.238949'),
                'longitude': Decimal('76.889709'),
            })
            
            description = descriptions.get(folder_name, f'''Уютный дом для комфортного отдыха. 

Идеально подходит для семейного отдыха или деловой поездки. 
Все удобства для комфортного проживания.''')

            # Создаем объявление
            listing_data = {
                'owner': user,
                'title': title,
                'description': description,
                'address': config['address'],
                'city': config['city'],
                'latitude': config['latitude'],
                'longitude': config['longitude'],
                'property_type': config['property_type'],
                'bedrooms': config['bedrooms'],
                'beds': config['beds'],
                'bathrooms': config['bathrooms'],
                'sqft': config['sqft'],
                'max_guests': config['max_guests'],
                'base_price': config['base_price'],
                'weekend_price': config['base_price'] * Decimal('1.2'),  # +20% на выходные
                'weekly_discount': 10,
                'monthly_discount': 20,
                'booking_type': 'instant',
                'min_nights': 1,
                'max_nights': 30,
                'house_rules': '''Правила дома:
• Запрещено курение внутри помещения
• Не шуметь после 23:00
• Уважайте соседей и окружающую среду
• Бережное отношение к имуществу''',
                'is_published': True,
                'is_verified': True,
                'moderation_status': 'approved',
            }

            listing = Listing.objects.create(**listing_data)

            # Копируем изображение
            from django.utils import timezone
            today = timezone.now()
            media_root = Path(settings.MEDIA_ROOT)
            target_path = media_root / 'photos' / str(today.year) / str(today.month).zfill(2) / str(today.day).zfill(2)
            target_path.mkdir(parents=True, exist_ok=True)
            
            target_file = target_path / source_image.name
            
            # Копируем файл
            shutil.copy2(source_image, target_file)
            
            # Присваиваем изображение объекту
            with open(target_file, 'rb') as f:
                listing.photo_main.save(source_image.name, File(f), save=True)

            # Добавляем удобства (временно отключено)
            # amenity_names = ['Wi-Fi', 'Парковка', 'Кухня', 'Кондиционер']
            # for amenity_name in amenity_names:
            #     if amenity_name in amenities_map:
            #         ListingAmenity.objects.get_or_create(
            #             listing=listing,
            #             amenity=amenities_map[amenity_name]
            #         )

            self.stdout.write(self.style.SUCCESS(f'[+] Создано объявление: {title} (ID: {listing.id})'))
            self.stdout.write(f'    Фото: {source_image.name}')
            created_count += 1

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Готово! Создано объявлений: {created_count}'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Пропущено (уже существуют): {skipped_count}'))
        self.stdout.write('='*50)

    # Временно отключено
    # def _get_or_create_amenities(self):
    #     """Получает или создает удобства"""
    #     amenities_data = [
    #         {'name': 'Wi-Fi', 'icon': 'wifi'},
    #         {'name': 'Парковка', 'icon': 'car'},
    #         {'name': 'Кондиционер', 'icon': 'snowflake'},
    #         {'name': 'Кухня', 'icon': 'utensils'},
    #         {'name': 'Стиральная машина', 'icon': 'washing-machine'},
    #         {'name': 'Телевизор', 'icon': 'tv'},
    #     ]
    # 
    #     amenities_map = {}
    #     for amenity_data in amenities_data:
    #         amenity, _ = Amenity.objects.get_or_create(
    #             name=amenity_data['name'],
    #             defaults={'icon': amenity_data['icon']}
    #         )
    #         amenities_map[amenity_data['name']] = amenity
    # 
    #     return amenities_map
