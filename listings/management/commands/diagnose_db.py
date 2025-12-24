# listings/management/commands/diagnose_db.py
from django.core.management.base import BaseCommand
from django.db import connection
from listings.models import Listing


class Command(BaseCommand):
    help = 'Диагностика состояния базы данных и объявлений'

    def handle(self, *args, **options):
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Диагностика базы данных'))
        self.stdout.write('='*60)
        
        cursor = connection.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.stdout.write(f'\nТаблицы в БД ({len(tables)}):')
        for table in tables:
            self.stdout.write(f'  - {table[0]}')
        
        try:
            cursor.execute("SELECT COUNT(*) FROM listings_listing")
            count = cursor.fetchone()
            self.stdout.write(f'\nЗаписей в listings_listing: {count[0]}')
            
            cursor.execute("SELECT COUNT(*) FROM listings_listing WHERE is_published=1")
            published_count = cursor.fetchone()
            self.stdout.write(f'Опубликованных: {published_count[0]}')
            
            cursor.execute("SELECT COUNT(*) FROM listings_listing WHERE is_published=0")
            unpublished_count = cursor.fetchone()
            self.stdout.write(f'Неопубликованных: {unpublished_count[0]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при проверке таблицы listings_listing: {e}'))
        
        try:
            cursor.execute("PRAGMA table_info(listings_listing)")
            columns = cursor.fetchall()
            self.stdout.write(f'\nКолонки в listings_listing ({len(columns)}):')
            for col in columns:
                self.stdout.write(f'  - {col[1]} ({col[2]})')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при получении структуры таблицы: {e}'))
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Проверка через Django ORM:')
        self.stdout.write('='*60)
        
        try:
            total_count = Listing.objects.count()
            self.stdout.write(f'\nВсего объявлений через ORM: {total_count}')
            
            published = Listing.objects.filter(is_published=True).count()
            self.stdout.write(f'Опубликованных: {published}')
            
            unpublished = Listing.objects.filter(is_published=False).count()
            self.stdout.write(f'Неопубликованных: {unpublished}')
            
            if total_count > 0:
                self.stdout.write('\nПервые 10 объявлений:')
                for listing in Listing.objects.all()[:10]:
                    status = '✓' if listing.is_published else '✗'
                    self.stdout.write(
                        f'  {status} ID:{listing.id} | {listing.title} | '
                        f'Город: {listing.city} | Цена: {listing.base_price}'
                    )
            else:
                self.stdout.write(self.style.WARNING('\n⚠ Объявления не найдены!'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nОшибка при проверке через ORM: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write('\n' + '='*60)

