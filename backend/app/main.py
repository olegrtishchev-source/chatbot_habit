"""Точка входа FastAPI-приложения."""

from fastapi import FastAPI

from app.routers import auth, habits

app = FastAPI(title="Chatbot Habit Tracker API")

app.include_router(auth.router)
app.include_router(habits.router)


@app.get("/health")
def read_health() -> dict[str, str]:
    """Проверка работоспособности сервиса."""
    return {"status": "ok"}
