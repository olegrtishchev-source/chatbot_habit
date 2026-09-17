FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.4.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY backend/app ./app
COPY backend/alembic.ini ./alembic.ini
COPY backend/migrations ./migrations

# при старте контейнера сначала применяем миграции, затем поднимаем сервер —
# так `docker-compose up` сразу даёт рабочую схему БД, без ручных шагов
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
