#Чтобы запустить сервер: 
#Запускаем venv: /Scripts/Activate
#Запускаем uvicorn: uvicorn check:app --reload

from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

app = FastAPI()

class CheckInput(BaseModel):
    token: str
    qrraw: str

@app.post("/nalog/")
def read_check(request: CheckInput):
    url = 'https://proverkacheka.com/api/v1/check/get'
    data = {
        'token': request.token,
        'qrraw': request.qrraw
    }
    
    try:
        response = requests.post(url, data=data, timeout=10)
        response.raise_for_status()
        api_response = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка запроса к API: {str(e)}")

    # Проверяем успешность ответа API
    if api_response.get('code') != 1:
        raise HTTPException(
            status_code=400,
            detail="API вернул ошибку: неверный QR-код или лимит запросов"
        )

    data_json = api_response.get('data', {}).get('json', {})
    if not data_json:
        raise HTTPException(status_code=500, detail="Нет данных чека в ответе")

    # Извлекаем информацию о магазине
    shop_name = data_json.get('retailPlace', 'Неизвестный магазин')
    user = data_json.get('user', '')

    # Формируем список товаров
    items = []
    for item in data_json.get('items', []):
        # Переводим цену и сумму из копеек в рубли
        price = item.get('price', 0) / 100
        total = item.get('sum', 0) / 100
        quantity = item.get('quantity', 1)
        
        items.append({
            "name": item.get('name', '').strip(),
            "price": round(price, 2),
            "quantity": quantity,
            "sum": round(total, 2)
        })

    # Итоговая сумма чека
    total_sum = data_json.get('totalSum', 0) / 100

    return {
        "shop": {
            "name": shop_name,
            "legal_name": user
        },
        "items": items,
        "total_sum": round(total_sum, 2),
        "datetime": data_json.get('dateTime')
    }

@app.get("/")
def root():
    return {"message": "Сервис парсинга чеков. Используйте POST /nalog/"}