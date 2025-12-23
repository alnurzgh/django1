"""
Настройки для PythonAnywhere (production)

Скопируйте нужные настройки в config/settings.py или импортируйте этот файл.
"""

# В settings.py добавьте в конец:

# Для PythonAnywhere
import os

# Автоматическое определение домена PythonAnywhere
if 'pythonanywhere.com' in os.environ.get('HTTP_HOST', ''):
    ALLOWED_HOSTS = [os.environ.get('HTTP_HOST', '')]
    DEBUG = False
else:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
    DEBUG = True

# Статические файлы
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Медиа файлы
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Безопасность для production
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # PythonAnywhere сам обрабатывает SSL
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

