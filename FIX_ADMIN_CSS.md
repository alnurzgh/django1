# Исправление проблемы с CSS админки на PythonAnywhere

## Проблема: Админка Django работает без стилей (CSS)

### Решение 1: Настройка Static files mapping на PythonAnywhere (РЕКОМЕНДУЕТСЯ)

1. **Войдите в панель управления PythonAnywhere**
2. **Перейдите в раздел "Web"**
3. **Найдите секцию "Static files"**
4. **Добавьте следующие mapping:**

   - **URL:** `/static/`
     **Directory:** `/home/ваш_username/django1/staticfiles`

   - **URL:** `/media/`
     **Directory:** `/home/ваш_username/django1/media`

5. **Нажмите кнопку "Reload"** (перезагрузите веб-приложение)

### Решение 2: Убедитесь, что выполнена команда collectstatic

В Bash консоли на PythonAnywhere выполните:

```bash
cd ~/django1
python manage.py collectstatic --noinput
```

Эта команда собирает все статические файлы (включая CSS админки) в папку `staticfiles/`.

### Решение 3: Проверьте настройки STATIC_ROOT в settings.py

Убедитесь, что в `config/settings.py` правильно настроены пути:

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

**Для PythonAnywhere можно использовать абсолютные пути:**

```python
STATIC_ROOT = '/home/ваш_username/django1/staticfiles'
MEDIA_ROOT = '/home/ваш_username/django1/media'
```

### Решение 4: Проверьте права доступа к папкам

```bash
cd ~/django1
chmod -R 755 staticfiles/
chmod -R 755 media/
```

### Быстрая проверка

1. **Проверьте, существует ли папка staticfiles:**
   ```bash
   ls -la ~/django1/staticfiles/
   ```

2. **Проверьте, есть ли там файлы админки:**
   ```bash
   ls -la ~/django1/staticfiles/admin/
   ```

3. **Если папка пустая или не существует:**
   ```bash
   cd ~/django1
   python manage.py collectstatic --noinput
   ```

4. **Проверьте настройки Static files в Web tab**

5. **Перезагрузите веб-приложение (Reload)**

### Типичные ошибки

1. **Папка staticfiles не создана или пустая**
   - Решение: Выполните `python manage.py collectstatic`

2. **Неправильный путь в Static files mapping**
   - Решение: Убедитесь, что путь указан как `/home/ваш_username/django1/staticfiles`

3. **Не перезагружено веб-приложение после изменений**
   - Решение: Нажмите "Reload" в Web tab

4. **DEBUG = False, но статические файлы не обслуживаются веб-сервером**
   - Решение: Настройте Static files mapping в Web tab (Решение 1)

### После исправления

Откройте админку: `https://ваш_username.pythonanywhere.com/admin/`

Стили должны загружаться корректно.

