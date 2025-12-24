# API Документация

## База URL
Все API endpoints находятся по адресу: `/api/`

## Аутентификация

API поддерживает два метода аутентификации:
1. **Session Authentication** - для веб-интерфейса
2. **Token Authentication** - для мобильных приложений и внешних интеграций

Для получения токена:
```bash
POST /api-auth/login/
# или через API:
POST /api/token/  # если используете djangorestframework-simplejwt
```

## Основные Endpoints

### 1. Поиск объектов (Listing)

#### Список всех объектов
```
GET /api/listings/
```

**Параметры запроса:**
- `city` - фильтр по городу
- `property_type` - тип недвижимости (apartment, house, room, studio, villa)
- `max_price` - максимальная цена за ночь
- `min_bedrooms` - минимальное количество спален
- `min_guests` - минимальное количество гостей
- `check_in` - дата заезда (YYYY-MM-DD) - фильтр по доступности
- `check_out` - дата выезда (YYYY-MM-DD) - фильтр по доступности
- `search` - поиск по названию, описанию, адресу
- `ordering` - сортировка (list_date, base_price, is_verified)

**Пример:**
```bash
GET /api/listings/?city=Алматы&check_in=2024-06-01&check_out=2024-06-10&max_price=15000
```

#### Поиск с фильтрами по доступности
```
POST /api/listings/search/
Content-Type: application/json

{
    "check_in": "2024-06-01",
    "check_out": "2024-06-10",
    "city": "Алматы",
    "max_price": 15000,
    "property_type": "apartment",
    "min_bedrooms": 2,
    "min_guests": 2
}
```

#### Детали объекта
```
GET /api/listings/{id}/
```

#### Проверка доступности объекта на даты
```
GET /api/listings/{id}/availability/?check_in=2024-06-01&check_out=2024-06-10
```

**Ответ:**
```json
{
    "available": true,
    "total_price": 135000.00,
    "nights": 9
}
```

#### Создание объекта (требует аутентификации)
```
POST /api/listings/
Content-Type: application/json
Authorization: Token {your_token}

{
    "title": "Уютная квартира в центре",
    "description": "Описание...",
    "address": "ул. Абая, 123",
    "city": "Алматы",
    "latitude": 43.238949,
    "longitude": 76.889709,
    "property_type": "apartment",
    "bedrooms": 2,
    "beds": 2,
    "bathrooms": 1.0,
    "sqft": 50,
    "max_guests": 4,
    "base_price": 10000,
    "weekend_price": 12000,
    "weekly_discount": 10,
    "monthly_discount": 20,
    "booking_type": "instant",
    "min_nights": 1,
    "max_nights": 30,
    "house_rules": "Не курить, не шуметь после 22:00",
    "amenity_ids": [1, 2, 3]
}
```

### 2. Бронирования (Booking)

#### Создание бронирования
```
POST /api/bookings/
Content-Type: application/json
Authorization: Token {your_token}

{
    "listing_id": 1,
    "check_in": "2024-06-01",
    "check_out": "2024-06-10",
    "guests_count": 2,
    "special_requests": "Поздний заезд после 20:00"
}
```

**Ответ при мгновенном бронировании:**
```json
{
    "id": 1,
    "listing": {...},
    "guest": {...},
    "check_in": "2024-06-01",
    "check_out": "2024-06-10",
    "guests_count": 2,
    "total_price": 90000.00,
    "status": "confirmed",
    "payment_status": "pending",
    "nights": 9
}
```

#### Мои бронирования (как гостя)
```
GET /api/bookings/my_bookings/
Authorization: Token {your_token}
```

#### Бронирования моих объектов (как владельца)
```
GET /api/bookings/my_listings_bookings/
Authorization: Token {your_token}
```

#### Подтверждение бронирования (владелец)
```
POST /api/bookings/{id}/confirm/
Authorization: Token {your_token}
```

#### Отклонение бронирования (владелец)
```
POST /api/bookings/{id}/reject/
Content-Type: application/json
Authorization: Token {your_token}

{
    "reason": "Объект уже занят на эти даты"
}
```

### 3. Отзывы (Review)

#### Список отзывов
```
GET /api/reviews/?listing=1
```

#### Создание отзыва (только для завершенных бронирований)
```
POST /api/reviews/
Content-Type: application/json
Authorization: Token {your_token}

{
    "booking_id": 1,
    "rating": 5,
    "comment": "Отличное место!",
    "cleanliness_rating": 5,
    "communication_rating": 5,
    "location_rating": 5,
    "value_rating": 5
}
```

### 4. Сообщения (Message)

#### Список сообщений
```
GET /api/messages/
Authorization: Token {your_token}
```

#### Создание сообщения
```
POST /api/messages/
Content-Type: application/json
Authorization: Token {your_token}

{
    "booking": 1,
    "recipient": 2,
    "listing": 1,
    "subject": "Вопрос о заезде",
    "content": "Здравствуйте, можно ли заехать пораньше?"
}
```

#### Пометить сообщение как прочитанное
```
POST /api/messages/{id}/mark_read/
Authorization: Token {your_token}
```

### 5. Удобства (Amenity)

#### Список всех удобств
```
GET /api/amenities/
```

### 6. iCal Синхронизация

#### Список синхронизаций для моих объектов
```
GET /api/ical-syncs/
Authorization: Token {your_token}
```

#### Создание iCal синхронизации
```
POST /api/ical-syncs/
Content-Type: application/json
Authorization: Token {your_token}

{
    "listing": 1,
    "url": "https://calendar.google.com/calendar/ical/example%40gmail.com/public/basic.ics",
    "is_active": true,
    "sync_frequency": 60
}
```

#### Синхронизация iCal календаря
```
POST /api/ical-syncs/{id}/sync/
Authorization: Token {your_token}
```

## Примеры использования

### Python (requests)
```python
import requests

BASE_URL = "http://localhost:8000/api"

# Поиск доступных объектов
response = requests.get(
    f"{BASE_URL}/listings/search/",
    json={
        "check_in": "2024-06-01",
        "check_out": "2024-06-10",
        "city": "Алматы",
        "max_price": 15000
    }
)
listings = response.json()

# Создание бронирования (с токеном)
headers = {"Authorization": "Token your_token_here"}
response = requests.post(
    f"{BASE_URL}/bookings/",
    json={
        "listing_id": 1,
        "check_in": "2024-06-01",
        "check_out": "2024-06-10",
        "guests_count": 2
    },
    headers=headers
)
booking = response.json()
```

### cURL
```bash
# Поиск объектов
curl -X POST "http://localhost:8000/api/listings/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "check_in": "2024-06-01",
    "check_out": "2024-06-10",
    "city": "Алматы"
  }'

# Создание бронирования
curl -X POST "http://localhost:8000/api/bookings/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_token_here" \
  -d '{
    "listing_id": 1,
    "check_in": "2024-06-01",
    "check_out": "2024-06-10",
    "guests_count": 2
  }'
```

## Обработка ошибок

API возвращает стандартные HTTP коды:
- `200` - Успешно
- `201` - Создано
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Ошибка сервера

Пример ответа с ошибкой:
```json
{
    "error": "Объект недоступен на выбранные даты"
}
```



