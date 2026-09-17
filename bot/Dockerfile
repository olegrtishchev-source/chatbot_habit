FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.4.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --only main

COPY bot/app ./app

CMD ["python", "-m", "app.main"]
