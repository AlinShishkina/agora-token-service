# переменные окружения
ENV_FILE_DEV = .env
ENV_FILE_PROD = .env.prod
COMPOSE_DEV = docker-compose.dev.yml
COMPOSE_PROD = docker-compose.prod.yml
PROJECT_NAME_DEV = agora-service-dev
PROJECT_NAME_PROD = agora-service-prod

# цели
.PHONY: help dev prod dev-build dev-up dev-down dev-logs dev-clean dev-status \
        dev-health dev-restart dev-shell prod-build prod-up prod-down prod-logs \
        prod-clean prod-status prod-health prod-restart prod-shell test-dev test-prod \
        setup-prod-env purge security-check init-db backup-db restore-db

help:
	@echo "Agora Token Service - Makefile"
	@echo ""
	@echo "РАЗРАБОТКА:"
	@echo "  make dev           - Запустить полное development окружение"
	@echo "  make dev-build     - Собрать development образы"
	@echo "  make dev-up        - Запустить development контейнеры"
	@echo "  make dev-down      - Остановить development"
	@echo "  make dev-logs      - Показать логи development"
	@echo "  make dev-status    - Статус контейнеров development"
	@echo "  make dev-health    - Проверить здоровье API development"
	@echo "  make dev-restart   - Перезапустить development"
	@echo "  make dev-shell     - Зайти в контейнер API development"
	@echo "  make dev-clean     - Очистить контейнеры и тома development"
	@echo ""
	@echo "ПРОД:"
	@echo "  make prod          - Запустить production окружение"
	@echo "  make prod-build    - Собрать production образы"
	@echo "  make prod-up       - Запустить production контейнеры"
	@echo "  make prod-down     - Остановить production"
	@echo "  make prod-logs     - Показать логи production"
	@echo "  make prod-status   - Статус контейнеров production"
	@echo "  make prod-health   - Проверить здоровье API production"
	@echo "  make prod-restart  - Перезапустить production"
	@echo "  make prod-shell    - Зайти в контейнер API production"
	@echo "  make prod-clean    - Очистить контейнеры и тома production"
	@echo ""
	@echo "ТЕСТИРОВАНИЕ:"
	@echo "  make test-dev      - Протестировать API development"
	@echo "  make test-prod     - Протестировать API production"
	@echo ""
	@echo "УТИЛИТЫ:"
	@echo "  make setup-prod-env- Создать/проверить .env.prod файл"
	@echo "  make security-check - Проверка безопасности конфигурации"
	@echo "  make init-db       - Инициализировать базу данных"
	@echo "  make backup-db     - Создать backup базы данных"
	@echo "  make restore-db    - Восстановить базу данных из backup"
	@echo "  make purge         - Полная очистка Docker (ОПАСНО!)"
	@echo ""


# DEV
dev: dev-build dev-up
	@echo ""
	@echo "Dev окружение запущено!"
	@echo "Документация: http://localhost:8000/docs"
	@echo "Health check: http://localhost:8000/health"

dev-build:
	@echo "Сборка dev образов..."
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_FILE_DEV) --project-name $(PROJECT_NAME_DEV) build --no-cache
	@echo "Dev образы собраны"

dev-up:
	@echo "Запуск dev окружения..."
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_FILE_DEV) --project-name $(PROJECT_NAME_DEV) up -d
	@echo "Ожидание запуска сервисов..."
	@for i in 1 2 3 4 5; do \
		echo "  Проверка... ($$i/5)"; \
		if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
			echo "API готов!"; \
			break; \
		fi; \
		sleep 5; \
		if [ $$i -eq 5 ]; then echo "API запускается дольше ожидаемого"; fi; \
	done
	docker compose -f $(COMPOSE_DEV) --project-name $(PROJECT_NAME_DEV) ps

dev-down:
	@echo "Остановка dev окружения..."
	docker compose -f $(COMPOSE_DEV) --env-file $(ENV_FILE_DEV) --project-name $(PROJECT_NAME_DEV) down
	@echo "Dev окружение остановлено"

dev-logs:
	@echo "Просмотр логов dev..."
	docker compose -f $(COMPOSE_DEV) --project-name $(PROJECT_NAME_DEV) logs -f

dev-clean:
	@echo "Очистка dev контейнеров и томов..."
	docker compose -f $(COMPOSE_DEV) --project-name $(PROJECT_NAME_DEV) down -v
	@echo "Dev очищено"

dev-status:
	@echo "Статус dev контейнеров:"
	docker compose -f $(COMPOSE_DEV) --project-name $(PROJECT_NAME_DEV) ps

dev-health:
	@echo "Проверка здоровья dev API..."
	@if curl -f http://localhost:8000/health >/dev/null 2>&1; then \
		curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health; \
		echo "Dev API здоров!"; \
	else \
		echo "Dev API не отвечает"; \
	fi

dev-restart: dev-down dev-up

dev-shell:
	@echo "Вход в контейнер API dev..."
	docker compose -f $(COMPOSE_DEV) --project-name $(PROJECT_NAME_DEV) exec api sh


# PROD
prod: check-prod-env prod-build prod-up
	@echo ""
	@echo "Production окружение запущено!"
	@echo "Health check: http://localhost:8001/health"

check-prod-env:
	@if [ ! -f "$(ENV_FILE_PROD)" ]; then \
		echo "Файл $(ENV_FILE_PROD) не найден!"; \
		echo "Создайте файл .env.prod с продовскими переменными"; \
		echo "Используйте: make setup-prod-env для создания шаблона"; \
		exit 1; \
	fi
	@echo "Файл $(ENV_FILE_PROD) найден"

prod-build:
	@echo "Сборка production образов..."
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_FILE_PROD) --project-name $(PROJECT_NAME_PROD) build --no-cache
	@echo "Production образы собраны"

prod-up:
	@echo "Запуск production окружения..."
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_FILE_PROD) --project-name $(PROJECT_NAME_PROD) up -d
	@echo "Ожидание запуска production сервисов..."
	@for i in 1 2 3 4 5 6; do \
		echo "  Проверка... ($$i/6)"; \
		if curl -s http://localhost:8001/health > /dev/null 2>&1; then \
			echo "Production API готов!"; \
			break; \
		fi; \
		sleep 10; \
		if [ $$i -eq 6 ]; then \
			echo "Production API запускается дольше ожидаемого"; \
			echo "Просмотр логов: make prod-logs"; \
		fi; \
	done
	docker compose -f $(COMPOSE_PROD) --project-name $(PROJECT_NAME_PROD) ps

prod-down:
	@echo "Остановка production окружения..."
	docker compose -f $(COMPOSE_PROD) --env-file $(ENV_FILE_PROD) --project-name $(PROJECT_NAME_PROD) down
	@echo "Production окружение остановлено"

prod-logs:
	@echo "Просмотр логов production..."
	docker compose -f $(COMPOSE_PROD) --project-name $(PROJECT_NAME_PROD) logs -f

prod-clean:
	@echo "Очистка production контейнеров и томов..."
	docker compose -f $(COMPOSE_PROD) --project-name $(PROJECT_NAME_PROD) down -v
	@echo "Production очищено"

prod-status:
	@echo "Статус production контейнеров:"
	docker compose -f $(COMPOSE_PROD) --project-name $(PROJECT_NAME_PROD) ps

prod-health:
	@echo "Проверка здоровья production API..."
	@if curl -f http://localhost:8001/health >/dev/null 2>&1; then \
		curl -s http://localhost:8001/health | jq . 2>/dev/null || curl -s http://localhost:8000/health; \
		echo "Production API здоров!"; \
	else \
		echo "Production API не отвечает"; \
	fi

prod-restart: prod-down prod-up

prod-shell:
	@echo "Вход в контейнер API production..."
	docker compose -f $(COMPOSE_PROD) --project-name $(PROJECT_NAME_PROD) exec api sh


test-dev:
	@echo "Тестирование dev API..."
	@if [ -f "./test_api.sh" ]; then \
		./test_api.sh; \
	else \
		echo "test_api.sh не найден"; \
		echo "Тестирование health check..."; \
		make dev-health; \
	fi

test-prod:
	@echo "Тестирование production API..."
	@if [ -f "./test_api.sh" ]; then \
		API_URL="http://localhost:8001" ./test_api.sh; \
	else \
		echo "test_api.sh не найден"; \
		echo "Тестирование health check..."; \
		make prod-health; \
	fi

# ============================================
# УТИЛИТЫ
# ============================================
setup-prod-env:
	@if [ -f "$(ENV_FILE_PROD)" ]; then \
		echo "Файл $(ENV_FILE_PROD) уже существует!"; \
		read -p "Перезаписать? (y/N): " confirm; \
		if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
			echo "Отменено."; \
			exit 0; \
		fi; \
	fi
	@echo "Создание шаблона $(ENV_FILE_PROD)..."
	@echo "# ============================================" > $(ENV_FILE_PROD)
	@echo "# ПРОД НАСТРОЙКИ - ИЗМЕНИТЬ ПЕРЕД ИСПОЛЬЗОВАНИЕМ!" >> $(ENV_FILE_PROD)
	@echo "# ============================================" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# Режим работы" >> $(ENV_FILE_PROD)
	@echo "ENVIRONMENT=production" >> $(ENV_FILE_PROD)
	@echo "DEBUG=false" >> $(ENV_FILE_PROD)
	@echo "LOG_LEVEL=warning" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# База данных" >> $(ENV_FILE_PROD)
	@echo "DB_NAME=agora_service_prod" >> $(ENV_FILE_PROD)
	@echo "DB_USER=agora_user_prod" >> $(ENV_FILE_PROD)
	@echo "DB_PASSWORD=СГЕНЕРИРУЙТЕ_СЛОЖНЫЙ_ПАРОЛЬ!" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# Redis" >> $(ENV_FILE_PROD)
	@echo "REDIS_PASSWORD=СГЕНЕРИРУЙТЕ_СЛОЖНЫЙ_ПАРОЛЬ!" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# Agora (реальные ключи!)" >> $(ENV_FILE_PROD)
	@echo "AGORA_APP_ID=ВАШ_НАСТОЯЩИЙ_APP_ID_ИЗ_CONSOLE.AGORA.IO" >> $(ENV_FILE_PROD)
	@echo "AGORA_APP_CERTIFICATE=ВАША_НАСТОЯЩАЯ_СЕРТИФИКАЦИЯ_ИЗ_CONSOLE.AGORA.IO" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# Безопасность" >> $(ENV_FILE_PROD)
	@echo "SECRET_KEY=django-insecure-СГЕНЕРИРУЙТЕ_НОВЫЙ_СЕКРЕТНЫЙ_КЛЮЧ" >> $(ENV_FILE_PROD)
	@echo "API_KEY=prod_СГЕНЕРИРУЙТЕ_НОВЫЙ_API_КЛЮЧ" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# CORS (укажите ваши домены)" >> $(ENV_FILE_PROD)
	@echo "CORS_ORIGINS=https://your-production-domain.com" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# Настройки Gunicorn" >> $(ENV_FILE_PROD)
	@echo "GUNICORN_WORKERS=4" >> $(ENV_FILE_PROD)
	@echo "GUNICORN_THREADS=2" >> $(ENV_FILE_PROD)
	@echo "GUNICORN_TIMEOUT=120" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "# ВНИМАНИЕ:" >> $(ENV_FILE_PROD)
	@echo "# 1. Замените все значения в ВЕРХНЕМ РЕГИСТРЕ на реальные" >> $(ENV_FILE_PROD)
	@echo "# 2. Никогда не коммитьте этот файл в репозиторий!" >> $(ENV_FILE_PROD)
	@echo "# 3. Установите права: chmod 600 $(ENV_FILE_PROD)" >> $(ENV_FILE_PROD)
	@echo "" >> $(ENV_FILE_PROD)
	@echo "   Шаблон $(ENV_FILE_PROD) создан!"
	@echo "   Отредактируйте файл перед использованием: nano $(ENV_FILE_PROD)"
	@echo "   Установите права: chmod 600 $(ENV_FILE_PROD)"

security-check:
	@echo " Проверка безопасности конфигурации..."
	@if [ -f "$(ENV_FILE_PROD)" ]; then \
		echo "Проверка $(ENV_FILE_PROD):"; \
		if grep -q "СГЕНЕРИРУЙТЕ\|ВАШ_НАСТОЯЩИЙ\|ВАША_НАСТОЯЩАЯ" $(ENV_FILE_PROD); then \
			echo " В $(ENV_FILE_PROD) есть незаполненные значения!"; \
		else \
			echo " $(ENV_FILE_PROD) заполнен корректно"; \
		fi; \
		if grep -q "DEBUG=true" $(ENV_FILE_PROD); then \
			echo "  ВНИМАНИЕ: DEBUG=true в production!"; \
		fi; \
		if grep -q "agora_password\|admin123\|dev-secret" $(ENV_FILE_PROD); then \
			echo "  ВНИМАНИЕ: Используются слабые пароли по умолчанию!"; \
		fi; \
	else \
		echo "ℹ  $(ENV_FILE_PROD) не найден, проверка пропущена"; \
	fi

init-db:
	@echo "  Инициализация базы данных..."
	@echo "Для development:"
	docker compose -f $(COMPOSE_DEV) exec postgres psql -U agora_user -d agora_service -c "\dt"
	@echo "Для production:"
	@if docker compose -f $(COMPOSE_PROD) ps | grep -q postgres; then \
		docker compose -f $(COMPOSE_PROD) exec postgres psql -U agora_user_prod -d agora_service_prod -c "\dt"; \
	else \
		echo "Production база данных не запущена"; \
	fi

backup-db:
	@echo " Создание backup базы данных..."
	@timestamp=$$(date +"%Y%m%d_%H%M%S"); \
	backup_file="backup_db_$${timestamp}.sql"; \
	echo "Backup файл: $${backup_file}"; \
	read -p "Development или Production? (d/P): " env; \
	if [ "$$env" = "d" ] || [ "$$env" = "D" ]; then \
		docker compose -f $(COMPOSE_DEV) exec postgres pg_dump -U agora_user agora_service > "$$backup_file"; \
		echo " Development backup создан: $${backup_file}"; \
	else \
		docker compose -f $(COMPOSE_PROD) exec postgres pg_dump -U agora_user_prod agora_service_prod > "$$backup_file"; \
		echo " Production backup создан: $${backup_file}"; \
	fi

restore-db:
	@echo " Восстановление базы данных из backup..."
	@read -p "Введите путь к backup файлу: " backup_file; \
	if [ ! -f "$$backup_file" ]; then \
		echo " Файл $$backup_file не найден"; \
		exit 1; \
	fi; \
	read -p "Dev или Production? (d/P): " env; \
	if [ "$$env" = "d" ] || [ "$$env" = "D" ]; then \
		echo "Восстановление dev базы..."; \
		docker compose -f $(COMPOSE_DEV) exec -T postgres psql -U agora_user agora_service < "$$backup_file"; \
		echo " Dev база восстановлена"; \
	else \
		echo "Восстановление production базы..."; \
		docker compose -f $(COMPOSE_PROD) exec -T postgres psql -U agora_user_prod agora_service_prod < "$$backup_file"; \
		echo " Production база восстановлена"; \
	fi

# Применять с осторожностью

purge:
	@echo "ПОЛНАЯ ОЧИСТКА DOCKER"
	@echo "Это удалит ВСЕ контейнеры, образы, тома и сети Docker"
	@read -p "Вы уверены? (yes/NO): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Остановка всех контейнеров..."; \
		docker stop $$(docker ps -aq) 2>/dev/null || true; \
		echo "Удаление контейнеров..."; \
		docker rm $$(docker ps -aq) 2>/dev/null || true; \
		echo "Удаление образов..."; \
		docker rmi $$(docker images -q) 2>/dev/null || true; \
		echo "Удаление томов..."; \
		docker volume rm $$(docker volume ls -q) 2>/dev/null || true; \
		echo "Удаление сетей..."; \
		docker network rm $$(docker network ls -q) 2>/dev/null || true; \
		echo "ВСЁ очищено!"; \
	else \
		echo "Отменено."; \
	fi

build: dev-build
up: dev-up
down: dev-down
logs: dev-logs
clean: dev-clean
status: dev-status
health: dev-health
restart: dev-restart
shell: dev-shell