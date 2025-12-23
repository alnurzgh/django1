# Быстрый старт для PythonAnywhere

## Быстрая установка (5 минут)

### 1. Загрузите проект

Через Git:
```bash
cd ~
git clone https://github.com/yourusername/my_rental_project.git
cd my_rental_project
```

Или загрузите через веб-интерфейс в папку `~/my_rental_project`

### 2. Настройте виртуальное окружение

```bash
cd ~/my_rental_project
python3.10 -m venv venv
source venv/bin/activate
pip install --user -r requirements.txt
```

### 3. Настройте базу данных

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 4. Настройте Web App

1. **Web** → **Add a new web app** → **Manual configuration** → **Python 3.10**

2. **WSGI configuration file** - замените содержимое на:

```python
import os
import sys

path = '/home/YOURUSERNAME/my_rental_project'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Замените YOURUSERNAME на ваш username!**

3. **Static files:**
   - URL: `/static/` → Directory: `/home/YOURUSERNAME/my_rental_project/staticfiles`
   - URL: `/media/` → Directory: `/home/YOURUSERNAME/my_rental_project/media`

4. **Нажмите Reload**

### 5. Обновите settings.py

Добавьте в `config/settings.py`:

```python
ALLOWED_HOSTS = ['YOURUSERNAME.pythonanywhere.com']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEBUG = False  # Для production
```

Готово! Откройте `https://YOURUSERNAME.pythonanywhere.com`

