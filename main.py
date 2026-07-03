"""
Точка входа в сервис.
Запускает веб-сервер Uvicorn с приложением FastAPI из пакета app.
"""
import uvicorn
from app import app  # импортируем готовое FastAPI-приложение из пакета app

# Настройки логирования: пишем логи сервера в файл server.log
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": "server.log",      # файл рядом с main.py
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["file"],
            "level": "INFO",               # уровень INFO: запросы, ошибки, старт
        },
    },
}

if __name__ == "__main__":
    # Запуск веб-сервера на локальном адресе, порт 8000
    uvicorn.run(
        "app:app",          # ссылка на приложение FastAPI внутри пакета app
        host="127.0.0.1",
        port=8000,
        log_config=log_config
    )