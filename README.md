# Agora Token Service

Микросервис для генерации токенов Agora (RTC, RTM, Dual) и управления видео-комнатами. Реализован на FastAPI с PostgreSQL и Docker.

## Описание

Сервис предоставляет API для:
- Простой аутентификации пользователей
- Генерации токенов Agora для видео-стримов и чата
- Создания и управления видео-комнатами
- Health checks и мониторинга

## Структура проекта

```
agora-token-service-python/
├── app/                    # Основное приложение FastAPI
│   ├── main.py            # Точка входа
│   ├── config.py          # Конфигурация
│   ├── database.py        # Подключение к БД
│   ├── models.py          # SQLAlchemy модели
│   ├── schemas.py         # Pydantic схемы
│   ├── routers/           # API роутеры
│   ├── services/          # Бизнес-логика
│   ├── crud/             # CRUD операции
│   └── utils/            # Утилиты (Agora токены, логирование)
├── alembic/               # Миграции БД
├── Dockerfile             # Docker образ
├── docker-compose.yml     # Разработка
├── docker-compose.prod.yml # Продакшн
└── requirements.txt       # Зависимости
```

## Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository>
cd agora-token-service-python
cp .env.example .env
```

### 2. Запуск через Docker Compose

```bash
docker compose up -d
```

Сервис будет доступен на `http://localhost:8001`

### 3. Миграции БД

```bash
docker compose exec api alembic upgrade head
```

### 4. Тестирование API одним скриптом

```bash
chmod +x test-api.sh
./test-api.sh
```

## Пример результата теста

```
Agora Token Service - Test
test_user_1766671671_163301 | http://localhost:8001
==============================================
1. Health Check:
{"status":"healthy","timestamp":1766671671.8536413,"database":"healthy","agora":"healthy","uptime":0.06955361366271973}
Code: 200
OK

2. Swagger Docs:
HTTP/1.1 200 OK
Code: 200
OK

3. Auth Check:
{"user_id":"test_user_1766671671_163301","authenticated":true,"timestamp":"2025-12-25T14:07:51.939949"}
Code: 200
OK

4. Create Room:
{"room_id":"dafeb8b8-6c39-47f6-a090-d80093b07a12","channel_name":"agora_channel_64e483cb258e","name":"Test Room 2025-12-25 17:07:51","is_private":false,"max_participants":10,"created_by":"test_user_1766671671_163301","created_at":"2025-12-25T14:07:51.983455Z"}
Code: 200
OK
Channel: agora_channel_64e483cb258e

5. RTC Token:
{"token":"006e9b9e5c0daba4abfbb7a2bf57485dbc5IABIDGXQGLphJvDhJNGH9FoMH42C59/ea2T5BbfXGPrhbjZeoF8mOfTLEABD2pMEuJZOaQEAAQBIU01p","expires_in":3600,"token_type":"rtc","channel":"agora_channel_64e483cb258e","uid":"123456789","role":"host","app_id":"e9b9e5c0daba4abfbb7a2bf57485dbc5","expire_timestamp":1766675272,"generated_at":1766671672}
Code: 200
OK

6. RTM Token:
{"token":"006e9b9e5c0daba4abfbb7a2bf57485dbc5IADQU5SOMoctu40k+r1guh1IRC3B7OMp0L5yrDYDcC0yayY59MsAAAAAEABLEmEAuJZOaQEA6AO4lk5p","expires_in":86400,"token_type":"rtm","uid":"123456789","app_id":"e9b9e5c0daba4abfbb7a2bf57485dbc5","expire_timestamp":1766758072,"generated_at":1766671672}
Code: 200
OK

7. Dual Tokens:
{"rtc":{"token":"...","expires_in":3600,...},"rtm":{"token":"...","expires_in":86400,...},"app_id":"e9b9e5c0daba4abfbb7a2bf57485dbc5","channel":"agora_channel_64e483cb258e","uid":"123456789","role":"host","combined_expire":1766675272,"generated_at":1766671672}
Code: 200
OK

==============================================
Result: 7/0 of 7
User ID: test_user_1766671671_163301
Channel: agora_channel_64e483cb258e
Docs: http://localhost:8001/docs

OK
docker compose logs api
```

## API Документация

Swagger UI: `http://localhost:8001/docs`

### Аутентификация
```
POST /api/simple
```
**Header:** `X-User-Id: <user_id>`

**Ответ:**
```json
{
  "user_id": "test_user_1766671671_163301",
  "authenticated": true,
  "timestamp": "2025-12-25T14:07:51.939949"
}
```

### Токены Agora

**RTC токен (видео)**
```
POST /api/tokens/rtc
```
```json
{
  "channel": "test_channel",
  "uid": "123456789",
  "role": "host"
}
```

**Ответ:**
```json
{
  "token": "006e9b9e5c0daba4abfbb7a2bf57485dbc5IABIDGXQGLphJvDhJNGH9FoMH42C59...",
  "expires_in": 3600,
  "token_type": "rtc",
  "channel": "agora_channel_64e483cb258e",
  "uid": "123456789",
  "role": "host",
  "app_id": "e9b9e5c0daba4abfbb7a2bf57485dbc5"
}
```

**RTM токен (чат)**
```
POST /api/tokens/rtm
```
```json
{
  "uid": "123456789"
}
```

**Dual токены (RTC + RTM)**
```
POST /api/tokens/dual
```

**Ответ:**
```json
{
  "rtc": { "token": "...", "expires_in": 3600, ... },
  "rtm": { "token": "...", "expires_in": 86400, ... },
  "app_id": "e9b9e5c0daba4abfbb7a2bf57485dbc5",
  "channel": "agora_channel_64e483cb258e",
  "uid": "123456789",
  "role": "host"
}
```

### Комнаты

**Создать комнату**
```
POST /api/rooms/
```
```json
{
  "name": "Test Room",
  "is_private": false,
  "max_participants": 10
}
```

**Ответ:**
```json
{
  "room_id": "dafeb8b8-6c39-47f6-a090-d80093b07a12",
  "channel_name": "agora_channel_64e483cb258e",
  "name": "Test Room 2025-12-25 17:07:51",
  "is_private": false,
  "max_participants": 10,
  "created_by": "test_user_1766671671_163301",
  "created_at": "2025-12-25T14:07:51.983455Z"
}
```

### Health Check
```
GET /health
GET /healthcheck
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": 1766671671.8536413,
  "database": "healthy",
  "agora": "healthy",
  "uptime": 0.06955361366271973
}
```

## Postman Коллекция

Скачайте полную коллекцию: [Agora Token Service.postman_collection.json](Agora_Token_Service.postman_collection.json)

### Переменные окружения
```
API_URL: http://localhost:8001
X-User-Id: test_user_123
channel: agora_channel_64e483cb258e
uid: 123456789
```

### Запросы в коллекции
1. `01 Health Check`
2. `02 Simple Auth`
3. `03 Create Room`
4. `04 RTC Token`
5. `05 RTM Token`
6. `06 Dual Tokens`

## Конфигурация

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost/agora_token

# Agora
AGORA_APP_ID=e9b9e5c0daba4abfbb7a2bf57485dbc5
AGORA_APP_CERTIFICATE=your_app_certificate

# FastAPI
SECRET_KEY=your_secret_key
```

## Деплой

### Development
```bash
docker compose up -d
```

### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

## Логи

```bash
docker compose logs api
docker compose logs db
```

## Разработка


### Скрипт тестирования

```bash
chmod +x test-api.sh
./test-api.sh
```


