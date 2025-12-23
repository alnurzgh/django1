"""
WSGI config для PythonAnywhere

Этот файл содержит WSGI конфигурацию для проекта.
Используйте этот файл как WSGI configuration file на PythonAnywhere.

Инструкция:
1. В разделе Web найдите "WSGI configuration file"
2. Откройте файл и замените содержимое на код из этого файла
3. Замените 'yourusername' на ваш username на PythonAnywhere
4. Убедитесь, что путь к проекту правильный
"""

import os
import sys

# Путь к проекту - ЗАМЕНИТЕ 'yourusername' на ваш username!
path = '/home/yourusername/my_rental_project'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

