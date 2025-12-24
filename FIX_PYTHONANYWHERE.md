# Исправление проблем на PythonAnywhere

## Проблема: Пропали все объявления и плохо работает админка

### Диагностика проблемы

1. **Подключитесь к консоли PythonAnywhere** (Bash console)

2. **Проверьте состояние базы данных:**
```bash
cd ~/django1
python manage.py shell
```

В shell выполните:
```python
from listings.models import Listing
print(f"Всего объявлений: {Listing.objects.count()}")
for listing in Listing.objects.all():
    print(f"ID: {listing.id}, Title: {listing.title}, Published: {listing.is_published}")
exit()
```

3. **Проверьте миграции:**
```bash
python manage.py showmigrations listings
```

4. **Проверьте логи ошибок:**
- Откройте Web tab в PythonAnywhere
- Посмотрите Error log

### Возможные решения

#### Решение 1: Проверка фильтрации в админке

Если объявления не отображаются из-за фильтра `is_published=False`:

```bash
python manage.py shell
```

```python
from listings.models import Listing
# Проверьте все объявления (даже неопубликованные)
all_listings = Listing.objects.all()
print(f"Всего записей: {all_listings.count()}")

# Если есть неопубликованные, опубликуйте их
for listing in Listing.objects.filter(is_published=False):
    listing.is_published = True
    listing.save()
    print(f"Опубликовано: {listing.title}")
```

#### Решение 2: Проверка настроек MEDIA_ROOT и MEDIA_URL

Убедитесь, что в `config/settings.py` правильные пути:

```python
# Для PythonAnywhere используйте абсолютные пути
MEDIA_ROOT = '/home/ваш_username/django1/media'
MEDIA_URL = '/media/'
```

И в WSGI файле должно быть:
```python
import os
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### Решение 3: Улучшение админки для отображения всех записей

Если проблема в админке, улучшим ее:

1. Обновите `listings/admin.py`:
```python
from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'base_price', 'is_published', 'is_verified', 'list_date')
    list_display_links = ('id', 'title')
    list_filter = ('is_published', 'is_verified', 'city', 'property_type')
    list_editable = ('is_published',)
    search_fields = ('title', 'description', 'address', 'city')
    list_per_page = 50
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Показываем все записи, не только опубликованные
        return qs
```

2. Примените изменения:
```bash
# Перезагрузите веб-приложение в Web tab
```

#### Решение 4: Если данные действительно пропали

Если объявления были потеряны, есть несколько вариантов:

**Вариант А: Восстановление из бэкапа (если есть)**
```bash
# Если у вас есть бэкап базы данных
cp db.sqlite3.backup db.sqlite3
python manage.py migrate
```

**Вариант Б: Создание тестовых данных**
```bash
python manage.py create_test_data
# Или
python manage.py create_listings_from_images
```

#### Решение 5: Проверка прав доступа к файлам

```bash
# Убедитесь, что у веб-сервера есть права на чтение БД и media
chmod 644 db.sqlite3
chmod -R 755 media/
chmod -R 755 staticfiles/
```

### Быстрая диагностика через команды

Создайте management команду для диагностики:

```bash
python manage.py shell
```

```python
from django.db import connection
cursor = connection.cursor()

# Проверьте все таблицы
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Таблицы в БД:", tables)

# Проверьте таблицу listings_listing
cursor.execute("SELECT COUNT(*) FROM listings_listing")
count = cursor.fetchone()
print(f"Записей в listings_listing: {count[0]}")

# Проверьте структуру таблицы
cursor.execute("PRAGMA table_info(listings_listing)")
columns = cursor.fetchall()
print("Колонки в listings_listing:")
for col in columns:
    print(f"  {col}")
```

### Настройка для PythonAnywhere (повторная проверка)

1. **STATIC_ROOT и MEDIA_ROOT должны быть абсолютными путями:**
```python
STATIC_ROOT = '/home/ваш_username/django1/staticfiles'
MEDIA_ROOT = '/home/ваш_username/django1/media'
```

2. **В WSGI файле добавьте обслуживание media файлов:**
```python
# В конец файла wsgi.py (для PythonAnywhere)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

3. **В Web tab настройте Static files:**
   - URL: `/static/` → `/home/ваш_username/django1/staticfiles`
   - URL: `/media/` → `/home/ваш_username/django1/media`

### Команды для быстрого исправления

```bash
# 1. Перейти в директорию проекта
cd ~/django1

# 2. Активировать виртуальное окружение (если используется)
source venv/bin/activate  # или workon django1

# 3. Применить миграции (если нужно)
python manage.py migrate

# 4. Создать суперпользователя (если нужно)
python manage.py createsuperuser

# 5. Собрать статические файлы
python manage.py collectstatic --noinput

# 6. Проверить целостность данных
python manage.py check

# 7. Перезагрузить веб-приложение в Web tab
```

### Проверка после исправления

1. Откройте админку: `https://ваш_username.pythonanywhere.com/admin/`
2. Проверьте раздел "Объявления" (Listings)
3. Убедитесь, что объявления отображаются
4. Проверьте главную страницу: `https://ваш_username.pythonanywhere.com/listings/`

