# listings/management/commands/check_static.py
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Проверка настройки статических файлов'

    def handle(self, *args, **options):
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Проверка статических файлов'))
        self.stdout.write('='*60)
        
        self.stdout.write(f'\nSTATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'STATIC_ROOT: {settings.STATIC_ROOT}')
        self.stdout.write(f'MEDIA_URL: {settings.MEDIA_URL}')
        self.stdout.write(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        
        static_root = Path(settings.STATIC_ROOT)
        media_root = Path(settings.MEDIA_ROOT)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Проверка директорий:')
        self.stdout.write('='*60)
        
        if static_root.exists():
            self.stdout.write(self.style.SUCCESS(f'\n[OK] STATIC_ROOT существует: {static_root}'))
            
            admin_static = static_root / 'admin'
            if admin_static.exists():
                css_files = list(admin_static.rglob('*.css'))
                js_files = list(admin_static.rglob('*.js'))
                self.stdout.write(f'  [OK] Папка admin существует')
                self.stdout.write(f'  [OK] CSS файлов: {len(css_files)}')
                self.stdout.write(f'  [OK] JS файлов: {len(js_files)}')
                
                if len(css_files) == 0:
                    self.stdout.write(self.style.WARNING('\n[WARNING] В папке admin нет CSS файлов!'))
                    self.stdout.write('  Выполните: python manage.py collectstatic --noinput')
                else:
                    self.stdout.write(f'  Примеры CSS файлов:')
                    for css in css_files[:3]:
                        self.stdout.write(f'    - {css.name}')
            else:
                self.stdout.write(self.style.ERROR(f'\n[ERROR] Папка admin не найдена в {static_root}'))
                self.stdout.write('  Выполните: python manage.py collectstatic --noinput')
        else:
            self.stdout.write(self.style.ERROR(f'\n[ERROR] STATIC_ROOT не существует: {static_root}'))
            self.stdout.write('  Создайте директорию и выполните: python manage.py collectstatic --noinput')
        
        if media_root.exists():
            self.stdout.write(self.style.SUCCESS(f'\n[OK] MEDIA_ROOT существует: {media_root}'))
        else:
            self.stdout.write(self.style.WARNING(f'\n[WARNING] MEDIA_ROOT не существует: {media_root}'))
            self.stdout.write('  Создайте директорию: mkdir -p media')
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Рекомендации для PythonAnywhere:')
        self.stdout.write('='*60)
        
        if not settings.DEBUG:
            self.stdout.write('\n[INFO] DEBUG = False')
            self.stdout.write('На PythonAnywhere необходимо настроить Static files mapping:')
            self.stdout.write('  1. Перейдите в Web tab')
            self.stdout.write('  2. Найдите секцию "Static files"')
            self.stdout.write(f'  3. Добавьте: URL="/static/" → Directory="{static_root}"')
            self.stdout.write(f'  4. Добавьте: URL="/media/" → Directory="{media_root}"')
            self.stdout.write('  5. Нажмите "Reload"')
        else:
            self.stdout.write('\n[INFO] DEBUG = True')
            self.stdout.write('Статические файлы обслуживаются Django (для разработки)')
        
        self.stdout.write('\n' + '='*60)

