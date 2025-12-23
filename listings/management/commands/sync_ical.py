# listings/management/commands/sync_ical.py
"""
Management команда для синхронизации всех активных iCal календарей

Использование:
    python manage.py sync_ical
    python manage.py sync_ical --listing-id 1  # Синхронизировать конкретный объект
"""
from django.core.management.base import BaseCommand
from listings.models import ICalSync
from listings.services import ICalSyncService


class Command(BaseCommand):
    help = 'Синхронизирует все активные iCal календари'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listing-id',
            type=int,
            help='ID объекта для синхронизации только его календарей',
        )
        parser.add_argument(
            '--ical-id',
            type=int,
            help='ID конкретной iCal синхронизации',
        )

    def handle(self, *args, **options):
        listing_id = options.get('listing_id')
        ical_id = options.get('ical_id')

        if ical_id:
            # Синхронизируем конкретную iCal синхронизацию
            try:
                ical_sync = ICalSync.objects.get(id=ical_id, is_active=True)
                self.stdout.write(f'Синхронизация iCal {ical_id} для объекта "{ical_sync.listing.title}"...')
                success, message = ICalSyncService.sync_ical(ical_sync)
                if success:
                    self.stdout.write(self.style.SUCCESS(f'✓ {message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ {message}'))
            except ICalSync.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'iCal синхронизация с ID {ical_id} не найдена или неактивна'))
        elif listing_id:
            # Синхронизируем все календари для конкретного объекта
            ical_syncs = ICalSync.objects.filter(listing_id=listing_id, is_active=True)
            if not ical_syncs.exists():
                self.stdout.write(self.style.WARNING(f'Активные iCal синхронизации для объекта {listing_id} не найдены'))
                return
            
            self.stdout.write(f'Синхронизация календарей для объекта {listing_id}...')
            for ical_sync in ical_syncs:
                self.stdout.write(f'  Синхронизация iCal {ical_sync.id}...')
                success, message = ICalSyncService.sync_ical(ical_sync)
                if success:
                    self.stdout.write(self.style.SUCCESS(f'    ✓ {message}'))
                else:
                    self.stdout.write(self.style.ERROR(f'    ✗ {message}'))
        else:
            # Синхронизируем все активные календари
            self.stdout.write('Синхронизация всех активных iCal календарей...')
            results = ICalSyncService.sync_all_active()
            
            success_count = sum(1 for r in results if r['success'])
            total_count = len(results)
            
            for result in results:
                status_style = self.style.SUCCESS if result['success'] else self.style.ERROR
                status_symbol = '✓' if result['success'] else '✗'
                self.stdout.write(
                    status_style(f'{status_symbol} {result["listing"]}: {result["message"]}')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\nЗавершено: {success_count}/{total_count} успешно')
            )


