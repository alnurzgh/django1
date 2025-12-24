# listings/management/commands/export_listing.py
import json
from django.core.management.base import BaseCommand
from django.core import serializers
from listings.models import Listing
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Экспорт объявления в JSON для импорта на PythonAnywhere'

    def add_arguments(self, parser):
        parser.add_argument(
            'listing_id',
            type=int,
            help='ID объявления для экспорта',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='listing_export.json',
            help='Имя выходного файла (по умолчанию: listing_export.json)',
        )
        parser.add_argument(
            '--include-owner',
            action='store_true',
            help='Включить информацию о владельце в экспорт',
        )

    def handle(self, *args, **options):
        listing_id = options['listing_id']
        output_file = options['output']
        include_owner = options['include_owner']

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Объявление с ID {listing_id} не найдено'))
            return

        self.stdout.write(f'Экспорт объявления: {listing.title} (ID: {listing.id})')

        export_data = {
            'listing': json.loads(serializers.serialize('json', [listing]))[0],
        }

        if include_owner and listing.owner:
            export_data['owner'] = json.loads(serializers.serialize('json', [listing.owner]))[0]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f'\n[OK] Объявление экспортировано в {output_file}'))
        self.stdout.write(f'\nДля импорта на PythonAnywhere:')
        self.stdout.write(f'1. Загрузите файл {output_file} на сервер')
        self.stdout.write(f'2. Выполните: python manage.py import_listing {output_file}')
        self.stdout.write(f'\nИли используйте команду:')
        self.stdout.write(f'python manage.py import_listing {output_file}')

