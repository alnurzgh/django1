# listings/management/commands/import_listing.py
import json
import os
from django.core.management.base import BaseCommand
from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from listings.models import Listing
from django.contrib.auth.models import User
from decimal import Decimal


class Command(BaseCommand):
    help = 'Импорт объявления из JSON файла (с PythonAnywhere или локально)'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Путь к JSON файлу с экспортированным объявлением',
        )
        parser.add_argument(
            '--owner-username',
            type=str,
            help='Username владельца (если нужно заменить)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Пропустить если объявление уже существует',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Обновить существующее объявление',
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        owner_username = options.get('owner_username')
        skip_existing = options['skip_existing']
        update_existing = options['update_existing']

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'Файл {json_file} не найден'))
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)

        listing_data = export_data['listing']
        listing_id = listing_data['pk']
        listing_fields = listing_data['fields'].copy()

        existing_listing = None
        try:
            existing_listing = Listing.objects.get(id=listing_id)
            if skip_existing:
                self.stdout.write(self.style.WARNING(f'Объявление с ID {listing_id} уже существует, пропускаем'))
                return
            elif update_existing:
                self.stdout.write(f'Обновление существующего объявления ID {listing_id}')
            else:
                self.stdout.write(self.style.ERROR(f'Объявление с ID {listing_id} уже существует'))
                self.stdout.write('Используйте --update-existing для обновления или --skip-existing для пропуска')
                return
        except Listing.DoesNotExist:
            self.stdout.write(f'Создание нового объявления')

        owner = None
        if owner_username:
            try:
                owner = User.objects.get(username=owner_username)
                self.stdout.write(f'Используется владелец: {owner.username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Пользователь {owner_username} не найден'))
                return
        elif 'owner' in export_data:
            owner_data = export_data['owner']
            owner_id = owner_data['pk']
            try:
                owner = User.objects.get(id=owner_id)
                self.stdout.write(f'Найден владелец: {owner.username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Владелец с ID {owner_id} не найден, объявление будет без владельца'))
        elif listing_fields.get('owner'):
            try:
                owner = User.objects.get(id=listing_fields['owner'])
                self.stdout.write(f'Найден владелец по ID: {owner.username}')
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Владелец с ID {listing_fields["owner"]} не найден, объявление будет без владельца'))
                listing_fields['owner'] = None

        listing_fields['owner'] = owner if owner else None

        photo_main_path = listing_fields.pop('photo_main', None)
        if photo_main_path and not update_existing:
            self.stdout.write(self.style.WARNING(f'Фото ({photo_main_path}) нужно загрузить отдельно в media/ на сервере'))

        if update_existing and existing_listing:
            for field, value in listing_fields.items():
                if field != 'id' and hasattr(existing_listing, field):
                    setattr(existing_listing, field, value)
            existing_listing.save()
            listing = existing_listing
            self.stdout.write(self.style.SUCCESS(f'[OK] Объявление обновлено: {listing.title} (ID: {listing.id})'))
        else:
            listing = Listing.objects.create(**listing_fields)
            self.stdout.write(self.style.SUCCESS(f'[OK] Объявление создано: {listing.title} (ID: {listing.id})'))

        self.stdout.write(f'\nОбъявление доступно по адресу:')
        self.stdout.write(f'/listings/{listing.id}/')
        if listing.is_published:
            self.stdout.write(self.style.SUCCESS('[OK] Объявление опубликовано'))
        else:
            self.stdout.write(self.style.WARNING('[WARNING] Объявление не опубликовано (is_published=False)'))

