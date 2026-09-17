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

### Аутентификация без пароля

У пользователя нет традиционного пароля и поля для его хранения — личность
подтверждает сам Telegram: бот аутентифицирует пользователя по его `telegram_id`
(`POST /auth/token`), backend выдаёт JWT на этот `id`, и токен запрашивается заново
при каждом обращении к API. Хранить и хешировать в этой схеме нечего: единственный
секрет — сам аккаунт Telegram пользователя, а не пароль в нашей базе.

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

### Ручное тестирование эндпоинтов из PowerShell

В Windows PowerShell 5.1 (не PowerShell 7) `Invoke-RestMethod` некорректно работает с
кириллицей: при отправке кодирует тело запроса не в UTF-8, а при получении ответа —
неверно угадывает кодировку JSON без явного `charset`. Данные в базе и в самом API
при этом остаются корректными (проверяется через `docker-compose exec db psql`) —
проблема только в клиенте, которым мы тестируем вручную. Реального бота (Python,
`httpx`) это не касается.

Чтобы кириллица корректно отправлялась и отображалась при ручных проверках:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001

function Send-JsonPost {
    param($Uri, $Headers, $Body, $Method = "Post")
    $json = $Body | ConvertTo-Json
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    Invoke-RestMethod -Uri $Uri -Method $Method -Headers $Headers -ContentType "application/json; charset=utf-8" -Body $bytes
}
```

### Локальный запуск бота (без Docker)

Backend должен быть уже запущен (см. выше). В отдельном окне:

```powershell
cd bot
$env:BACKEND_BASE_URL = "http://127.0.0.1:8000"
poetry run python -m app.main
```

Важно: именно `127.0.0.1`, а не `localhost`. На некоторых машинах Windows `localhost`
из Python (`httpx`) резолвится иначе, чем из PowerShell, и запросы к backend
получают пустой `503` — тогда как `127.0.0.1` работает всегда одинаково.

Бот держит соединение открытым (long-polling к Telegram) — не закрывай окно, пока
он должен работать. Если нужно перезапустить, всегда `Ctrl+C` и запуск той же
командой в этом же окне, а не открытие нового: два параллельных экземпляра бота
одновременно опрашивают Telegram и получают ошибку 409 Conflict.

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
