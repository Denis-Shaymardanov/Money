from fastapi import FastAPI
from .api.endpoints import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Сервис парсинга чеков и конвертации PDF в CSV с категоризацией"}