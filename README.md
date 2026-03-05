# Crypto Currency Service

## О проекте

**Crypto Currency Service** — это легковесный микросервис на Python (FastAPI), который предоставляет REST API для получения актуальных курсов криптовалют. Сервис использует публичное API CoinGecko, не требует API ключа и упакован в Docker-контейнер для простого развертывания.

## Быстрый старт

### Вариант 1: Docker Hub (рекомендуется)

Самый простой способ запустить сервис — использовать готовый образ с Docker Hub:

Ссылка на образ: https://hub.docker.com/r/lkmatter/crypto-service

```bash
# 1. Скачать образ
docker pull lkmatter/crypto-service:latest

# 2. Создать файл .env с вашими настройками
cat > .env << EOF
VERSION=1.0.0
PORT=8000
EOF

# 3. Запустить контейнер
docker run -d \
  --name crypto-app \
  -p 8000:8000 \
  --env-file .env \
  lkmatter/crypto-service:latest

# 4. Проверить, что сервис работает
curl http://localhost:8000/health
```

### Вариант 2: Сборка из исходников с Docker Compose

```bash
# 1. Клонировать репозиторий
git clone https://github.com/benchiz/crypto-currency-app.git
cd crypto-currency-app

# 2. Создать файл .env
cat > .env << EOF
VERSION=1.0.0
PORT=8000
EOF

# 3. Запустить через Docker Compose
docker-compose up -d --build

# 4. Проверить логи
docker-compose logs -f
```

### Вариант 3: Локальный запуск (без Docker)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/benchiz/crypto-currency-app.git
cd crypto-currency-app

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# venv\Scripts\activate   # для Windows

# 3. Установить зависимости
pip install -r app/requirements.txt

# 4. Создать .env файл
cat > .env << EOF
VERSION=1.0.0
PORT=8000
EOF

# 5. Запустить сервер
cd app
python main.py
```

После запуска откройте браузер и перейдите по адресу:
- Swagger UI (документация): http://localhost:8000/docs
- Health check: http://localhost:8000/health