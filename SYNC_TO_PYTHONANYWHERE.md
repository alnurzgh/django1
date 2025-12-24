# Синхронизация объявлений на PythonAnywhere

## Способ 1: Экспорт/Импорт через JSON (РЕКОМЕНДУЕТСЯ)

### На локальной машине:

1. **Экспортируйте объявление:**
   ```bash
   python manage.py export_listing <ID_объявления> --output listing_export.json
   ```
   
   Пример:
   ```bash
   python manage.py export_listing 1 --output listing_export.json
   ```

2. **Если нужно включить информацию о владельце:**
   ```bash
   python manage.py export_listing 1 --include-owner --output listing_export.json
   ```

3. **Загрузите файл `listing_export.json` на PythonAnywhere:**
   - Через веб-интерфейс Files
   - Или через SCP/SFTP
   - Или скопируйте содержимое файла

### На PythonAnywhere:

1. **Сохраните JSON файл** в директорию проекта:
   ```bash
   cd ~/django1
   # Загрузите listing_export.json в эту директорию
   ```

2. **Импортируйте объявление:**
   ```bash
   python manage.py import_listing listing_export.json
   ```

3. **Если нужно назначить другого владельца:**
   ```bash
   python manage.py import_listing listing_export.json --owner-username имя_пользователя
   ```

4. **Если объявление уже существует:**
   ```bash
   # Обновить существующее
   python manage.py import_listing listing_export.json --update-existing
   
   # Или пропустить
   python manage.py import_listing listing_export.json --skip-existing
   ```

## Способ 2: Использование Django dumpdata/loaddata

### На локальной машине:

1. **Экспортируйте объявление:**
   ```bash
   python manage.py dumpdata listings.Listing --pks <ID> --indent 2 > listing_export.json
   ```
   
   Пример:
   ```bash
   python manage.py dumpdata listings.Listing --pks 1 --indent 2 > listing_export.json
   ```

2. **Загрузите файл на PythonAnywhere**

### На PythonAnywhere:

1. **Импортируйте данные:**
   ```bash
   python manage.py loaddata listing_export.json
   ```

## Способ 3: Создание объявления через админку на PythonAnywhere

1. Откройте админку: `https://ваш_username.pythonanywhere.com/admin/`
2. Перейдите в раздел "Объявления"
3. Нажмите "Добавить объявление"
4. Заполните все поля вручную
5. Сохраните

## Способ 4: Использование команды create_listings_from_images

Если у вас есть папка с изображениями:

1. **Загрузите папку с изображениями** на PythonAnywhere (например, `img/`)
2. **Выполните команду:**
   ```bash
   cd ~/django1
   python manage.py create_listings_from_images
   ```

## Полезные команды

### Проверка объявлений на PythonAnywhere:

```bash
python manage.py shell
```

```python
from listings.models import Listing
# Посмотреть все объявления
for listing in Listing.objects.all():
    print(f"ID: {listing.id}, Title: {listing.title}, Published: {listing.is_published}")

# Посчитать объявления
print(f"Всего: {Listing.objects.count()}")
print(f"Опубликованных: {Listing.objects.filter(is_published=True).count()}")
```

### Экспорт всех объявлений:

```bash
python manage.py dumpdata listings.Listing --indent 2 > all_listings.json
```

### Импорт всех объявлений:

```bash
python manage.py loaddata all_listings.json
```

## Важные замечания

1. **Фотографии:** При экспорте/импорте через JSON путь к фото сохраняется, но само изображение нужно загрузить отдельно в папку `media/` на PythonAnywhere.

2. **Владелец:** Если пользователь с таким ID не существует на PythonAnywhere, объявление будет создано без владельца. Используйте `--owner-username` для назначения существующего пользователя.

3. **ID объявления:** Если объявление с таким ID уже существует, используйте `--update-existing` для обновления или `--skip-existing` для пропуска.

4. **База данных:** Экспорт/импорт работает только для SQLite. Для других БД используйте соответствующие инструменты.

