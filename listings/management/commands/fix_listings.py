# listings/management/commands/fix_listings.py
from django.core.management.base import BaseCommand
from listings.models import Listing


class Command(BaseCommand):
    help = 'Исправление проблем с объявлениями: публикация всех, проверка данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--publish-all',
            action='store_true',
            help='Опубликовать все неопубликованные объявления',
        )
        parser.add_argument(
            '--verify-all',
            action='store_true',
            help='Верифицировать все объявления',
        )
        parser.add_argument(
            '--fix-empty',
            action='store_true',
            help='Исправить пустые обязательные поля',
        )

    def handle(self, *args, **options):
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Исправление объявлений'))
        self.stdout.write('='*60)
        
        total = Listing.objects.count()
        self.stdout.write(f'\nВсего объявлений в базе: {total}')
        
        if total == 0:
            self.stdout.write(self.style.WARNING('\n⚠ Объявления не найдены!'))
            self.stdout.write('Создайте объявления через:')
            self.stdout.write('  python manage.py create_test_data')
            self.stdout.write('  python manage.py create_listings_from_images')
            return
        
        if options['publish_all']:
            unpublished = Listing.objects.filter(is_published=False)
            count = unpublished.count()
            if count > 0:
                unpublished.update(is_published=True)
                self.stdout.write(self.style.SUCCESS(f'\n✓ Опубликовано объявлений: {count}'))
            else:
                self.stdout.write('\n✓ Все объявления уже опубликованы')
        
        if options['verify_all']:
            unverified = Listing.objects.filter(is_verified=False)
            count = unverified.count()
            if count > 0:
                unverified.update(is_verified=True)
                self.stdout.write(self.style.SUCCESS(f'\n✓ Верифицировано объявлений: {count}'))
            else:
                self.stdout.write('\n✓ Все объявления уже верифицированы')
        
        if options['fix_empty']:
            from decimal import Decimal
            fixed = 0
            
            from django.db.models import Q
            listings = Listing.objects.filter(
                Q(base_price__isnull=True) | 
                Q(base_price=0) |
                Q(city='') |
                Q(address='')
            )
            
            for listing in listings:
                if not listing.base_price or listing.base_price == 0:
                    listing.base_price = Decimal('10000.00')
                    fixed += 1
                if not listing.city:
                    listing.city = 'Алматы'
                    fixed += 1
                if not listing.address:
                    listing.address = 'Адрес не указан'
                    fixed += 1
                listing.save()
            
            if fixed > 0:
                self.stdout.write(self.style.SUCCESS(f'\n✓ Исправлено объявлений: {fixed}'))
            else:
                self.stdout.write('\n✓ Нет объявлений с пустыми полями')
        
        if not any([options['publish_all'], options['verify_all'], options['fix_empty']]):
            self.stdout.write('\nДоступные опции:')
            self.stdout.write('  --publish-all  : Опубликовать все объявления')
            self.stdout.write('  --verify-all   : Верифицировать все объявления')
            self.stdout.write('  --fix-empty    : Исправить пустые поля')
            self.stdout.write('\nПример: python manage.py fix_listings --publish-all')
        
        published_count = Listing.objects.filter(is_published=True).count()
        verified_count = Listing.objects.filter(is_verified=True).count()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Текущая статистика:')
        self.stdout.write(f'  Всего: {total}')
        self.stdout.write(f'  Опубликованных: {published_count}')
        self.stdout.write(f'  Верифицированных: {verified_count}')
        self.stdout.write('='*60)

