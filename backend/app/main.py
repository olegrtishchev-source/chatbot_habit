"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI

app = FastAPI(title="Chatbot Habit Tracker API")


@app.get("/health")
def read_health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}
