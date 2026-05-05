import uvicorn
from check import app 

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
            "filename": "server.log",          # ← файл логов рядом с exe
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["file"],
            "level": "INFO",
        },
    },
}

if __name__ == "__main__":
    uvicorn.run(
        "check:app",
        host="127.0.0.1",
        port=8000,
        log_config=log_config
    )