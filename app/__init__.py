"""
Пакет app – основное приложение FastAPI.
Здесь создаётся экземпляр FastAPI и подключается роутер с эндпоинтами.
"""
from fastapi import FastAPI
from .api.endpoints import router  # импортируем роутер из модуля endpoints

app = FastAPI()                     # создаём экземпляр приложения
app.include_router(router)          # подключаем маршруты (pdftocsv_json, check, ...)

@app.get("/")
def root():
    """Корневой эндпоинт – проверка работоспособности сервера."""
    return {"message": "Сервис парсинга чеков и конвертации PDF в CSV с категоризацией"}