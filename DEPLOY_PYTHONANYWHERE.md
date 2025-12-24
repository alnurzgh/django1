# Деплой на PythonAnywhere

Пошаговая инструкция по развертыванию проекта на PythonAnywhere.

## Подготовка проекта

1. **Убедитесь, что все зависимости указаны в requirements.txt**
   ```bash
   pip freeze > requirements.txt
   ```

2. **Создайте файл с production настройками** (опционально)
   - Используйте `config/settings.py` с настройками для production

## Шаги деплоя на PythonAnywhere

### 1. Создайте аккаунт на PythonAnywhere

Перейдите на https://www.pythonanywhere.com и зарегистрируйтесь.

### 2. Откройте Bash консоль

В панели управления выберите "Bash" для доступа к консоли.

### 3. Клонируйте проект (если используете Git)

```bash
cd ~
git clone https://github.com/yourusername/django1.git
cd django1
```

**Или загрузите файлы вручную:**

1. Перейдите в "Files"
2. Создайте папку `django1` в домашней директории
3. Загрузите все файлы проекта через веб-интерфейс

### 4. Создайте виртуальное окружение

```bash
cd ~/django1
python3.10 -m venv venv
source venv/bin/activate
```

### 5. Установите зависимости

```bash
pip install --user -r requirements.txt
```

### 6. Настройте базу данных

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Соберите статические файлы

```bash
python manage.py collectstatic --noinput
```

### 8. Настройте Web App

1. Перейдите в раздел **"Web"** в панели управления
2. Нажмите **"Add a new web app"**
3. Выберите домен (например, `yourusername.pythonanywhere.com`)
4. Выберите **"Manual configuration"** -> **"Python 3.10"** (или новее)

### 9. Настройте WSGI файл

В разделе Web найдите секцию "WSGI configuration file" и откройте файл (обычно `/var/www/yourusername_pythonanywhere_com_wsgi.py`).

Замените содержимое на:

```python
import os
import sys

path = '/home/yourusername/django1'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Важно:** Замените `yourusername` на ваш username на PythonAnywhere!

### 10. Настройте статические файлы

В разделе Web найдите секцию "Static files":

1. **URL:** `/static/`
   **Directory:** `/home/yourusername/django1/staticfiles`

2. **URL:** `/media/`
   **Directory:** `/home/yourusername/django1/media`

### 11. Обновите settings.py

Убедитесь, что в `config/settings.py` есть следующие настройки:

```python
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEBUG = False  # Для production
```

### 12. Создайте необходимые директории

```bash
mkdir -p staticfiles
mkdir -p media/photos
```

### 13. Перезагрузите Web App

В разделе Web нажмите кнопку **"Reload"** рядом с вашим доменом.

### 14. Проверьте работу

Откройте в браузере: `https://yourusername.pythonanywhere.com`

## Дополнительные настройки

### Настройка расписания для синхронизации iCal

1. Перейдите в раздел **"Tasks"**
2. Добавьте задачу (например, ежедневная синхронизация в 3:00):

```bash
source /home/yourusername/django1/venv/bin/activate
cd /home/yourusername/django1
python manage.py sync_ical
```

### Настройка email (опционально)

В `config/settings.py` добавьте настройки для отправки email:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Решение проблем

### Ошибка 500

1. Проверьте логи ошибок в разделе Web -> Error log
2. Убедитесь, что все зависимости установлены
3. Проверьте, что база данных мигрирована
4. Убедитесь, что DEBUG = False в settings.py

### Статические файлы не загружаются

1. Проверьте настройки Static files в разделе Web
2. Убедитесь, что выполнили `collectstatic`
3. Проверьте права доступа к папке staticfiles

### База данных не работает

1. Убедитесь, что используете SQLite (по умолчанию)
2. Для PostgreSQL/MySQL потребуется настройка в разделе Databases

## Полезные команды

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Создать суперпользователя
python manage.py createsuperuser

# Применить миграции
python manage.py migrate

# Собрать статические файлы
python manage.py collectstatic --noinput

# Запустить shell
python manage.py shell

# Просмотреть логи
tail -f /var/log/yourusername.pythonanywhere.com.error.log
```

## Безопасность

⚠️ **Важно для production:**

1. Измените `SECRET_KEY` в settings.py на случайную строку
2. Установите `DEBUG = False`
3. Настройте `ALLOWED_HOSTS` правильно
4. Используйте HTTPS (включено по умолчанию на PythonAnywhere)
5. Не коммитьте `settings.py` с реальным SECRET_KEY в Git

## Обновление проекта

После обновления кода:

1. Загрузите новые файлы
2. Активируйте виртуальное окружение
3. Установите новые зависимости (если есть): `pip install -r requirements.txt`
4. Примените миграции: `python manage.py migrate`
5. Соберите статические файлы: `python manage.py collectstatic --noinput`
6. Перезагрузите Web App


