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
├── docker-compose.dev.yml # Разработка
├── docker-compose.prod.yml # Продакшн
├── .env                   # Dev переменные окружения
├── .env.prod              # Prod переменные окружения (НЕ коммитить!)
├── Makefile               # Управление окружениями
├── test_api.sh            # Тестовый скрипт
└── requirements.txt       # Зависимости
```

## Быстрый старт

### 1. Клонирование и установка

```bash
git clone <repository>
cd agora-token-service-python
cp .env.example .env
```

**!Примечание!** Лучше всего запускать через **Makefile** - он автоматически управляет dev/prod окружениями, проверяет health, создает конфиги и предоставляет удобные команды для тестирования, логов и деплоя.

### 2. Запуск через Makefile (рекомендуется)

```bash
# Development (порт 8000)
make dev

# Production (порт 8001) 
make prod
```

Сервис будет доступен:
- **Dev**: `http://localhost:8000`
- **Prod**: `http://localhost:8001`

### 3. Альтернатива: Docker Compose напрямую

```bash
# Development
docker compose -f docker-compose.dev.yml --env-file .env up -d --build

# Production  
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### 4. Тестирование API одним скриптом

```bash
chmod +x test_api.sh
./test_api.sh
```

## Полный список Makefile команд

```bash
make help
```

**Основные команды:**
```
РАЗРАБОТКА:          make dev, dev-up, dev-logs, dev-health, dev-clean
ПРОДАКШН:            make prod, prod-up, prod-logs, prod-health  
ТЕСТИРОВАНИЕ:        make test-dev, test-prod
УТИЛИТЫ:             make setup-prod-env, security-check, backup-db
```

## Пример результата теста

```
Agora Token Service - Test
test_user_1766671671_163301 | http://localhost:8001
==============================================
1. Health Check: [...] Code: 200 ✓ OK
2. Swagger Docs: [...] Code: 200 ✓ OK  
3. Auth Check: [...] Code: 200 ✓ OK
4. Create Room: [...] Code: 200 ✓ OK
Channel: agora_channel_64e483cb258e
5. RTC Token: [...] Code: 200 ✓ OK
6. RTM Token: [...] Code: 200 ✓ OK
7. Dual Tokens: [...] Code: 200 ✓ OK
==============================================
Result: 7/0 of 7
Docs: http://localhost:8001/docs
✓ ALL TESTS PASSED
docker compose logs api
```

## API Документация

Swagger UI: `http://localhost:8001/docs` (prod) / `http://localhost:8000/docs` (dev)

### Аутентификация
```
POST /api/auth
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

### Health Check
```
GET /health
GET /healthcheck
```

## Postman Коллекция

Скачайте полную коллекцию: [Agora Token Service.postman_collection.json](https://web.postman.co/workspace/My-Workspace~918906d3-d116-4030-8f3a-bec45c62fcf0/collection/39461817-008ae5bf-b231-4f7d-86d1-03e8a1dd2f3c?action=share&source=copy-link&creator=39461817)


**Переменные окружения:**
```
API_URL: http://localhost:8001
X-User-Id: test_user_123
channel: agora_channel_64e483cb258e
uid: 123456789
```

## Конфигурация

### Development (.env)
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=info
DATABASE_URL=postgresql://agora_user:agora_pass@localhost:5432/agora_service
AGORA_APP_ID=e9b9e5c0daba4abfbb7a2bf57485dbc5
AGORA_APP_CERTIFICATE=your_app_certificate
```

### Production (.env.prod) - создается командой `make setup-prod-env`
```bash
make setup-prod-env  # Создает шаблон .env.prod
```

## Деплой

| Цель | Команда | Порт | docker-compose.yml |
|------|---------|------|-------------------|
| **Development** | `make dev` | 8000 | docker-compose.dev.yml |
| **Production** | `make prod` | 8001 | docker-compose.prod.yml |

### Быстрые команды
```bash
make dev          # Dev окружение (рекомендуется)
make prod         # Prod окружение
make dev-logs     # Логи dev
make test-dev     # Тест dev API  
make dev-down     # Остановить dev
make dev-clean    # Полная очистка dev
```

## Логи

```bash
# Development
make dev-logs

# Production  
make prod-logs

# Или напрямую
docker compose -f docker-compose.dev.yml logs api -f
docker compose -f docker-compose.prod.yml logs api -f
```

## Разработка

### Скрипт тестирования
```bash
# Development
make test-dev

# Production 
make test-prod

# Прямо
chmod +x test_api.sh
./test_api.sh
```

### Полезные утилиты
```bash
make security-check    # Проверка .env.prod
make backup-db         # Бэкап БД  
make init-db           # Показать таблицы БД
make setup-prod-env    # Создать .env.prod
```
