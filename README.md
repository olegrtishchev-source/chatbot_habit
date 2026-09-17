# Чат-бот для трекинга привычек

Практикум Skillbox, курс «Python-фреймворк Django» (кейс). Telegram-бот для управления
привычками по заказу центра подбора психологов.

## Архитектура

Проект разбит на три независимых сервиса (MVP/MVC), поднимаемых через `docker-compose`:

- `backend/` — FastAPI-сервис: хранение и обработка данных (SQLAlchemy + PostgreSQL,
  миграции через Alembic), аутентификация и авторизация бота по токену.
- `bot/` — Telegram-бот (pyTelegramBotAPI), слой представления: команды пользователя,
  вся работа с данными — через HTTP-запросы к `backend`.
- `scheduler/` — фоновый сервис оповещений: напоминания пользователям и перенос
  невыполненных привычек на следующий день.

## Стек

Poetry, PostgreSQL, SQLAlchemy, Alembic, pyTelegramBotAPI, FastAPI, PyJWT, APScheduler,
Docker Compose.

## Разработка (локально, без Docker)

БД поднимается в Docker в любом случае, приложение — локально через Poetry.

Контейнер `db` слушает порт `5433` на хосте (не `5432` — порт мог быть занят
нативной службой PostgreSQL на Windows). Для подключения с хоста нужно
переопределить `DATABASE_URL`, указав `localhost:5433` вместо `db:5432`
из `.env`:

```powershell
docker-compose up -d db
poetry install
cd backend
$env:DATABASE_URL = "postgresql+psycopg://chatbot_habit:<пароль_из_.env>@localhost:5433/chatbot_habit"
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Новая миграция после изменения моделей:

```powershell
cd backend
poetry run alembic revision --autogenerate -m "описание изменения"
```

## Запуск всего стека

```powershell
copy .env.example .env
# заполнить .env: пароль БД, TELEGRAM_BOT_TOKEN (от @BotFather), JWT_SECRET_KEY
docker-compose up --build
```

## Проверка качества кода

```powershell
poetry run ruff check .
poetry run ruff format --check .
```

`mypy` нужно запускать отдельно на каждом сервисе (а не из корня) — все три
сервиса используют одинаковое имя пакета `app`, и из корня mypy принимает их
за один и тот же модуль:

```powershell
cd backend; poetry run mypy app; cd ..
cd bot; poetry run mypy app; cd ..
cd scheduler; poetry run mypy app; cd ..
```
