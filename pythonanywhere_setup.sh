#!/bin/bash
# Скрипт для быстрой настройки на PythonAnywhere
# Запустите: bash pythonanywhere_setup.sh

echo "Настройка проекта для PythonAnywhere..."

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install --user -r requirements.txt

# Применяем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Создаем необходимые директории
mkdir -p staticfiles
mkdir -p media/photos

echo "Готово! Не забудьте:"
echo "1. Обновить ALLOWED_HOSTS в config/settings.py"
echo "2. Установить DEBUG = False для production"
echo "3. Настроить WSGI файл на PythonAnywhere"
echo "4. Настроить Static files в разделе Web"


