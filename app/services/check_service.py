import requests

class CheckService:
    BASE_URL = 'https://proverkacheka.com/api/v1/check/get'

    def get_check_data(self, token: str, qrraw: str) -> dict:
        try:
            response = requests.post(self.BASE_URL, data={'token': token, 'qrraw': qrraw}, timeout=10)
            response.raise_for_status()
            api_response = response.json()
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Ошибка запроса к API: {e}")

        if api_response.get('code') != 1:
            raise ValueError("API вернул ошибку: неверный QR-код или лимит запросов")

        data_json = api_response.get('data', {}).get('json', {})
        if not data_json:
            raise ValueError("Нет данных чека в ответе")

        shop_name = data_json.get('retailPlace', 'Неизвестный магазин')
        user = data_json.get('user', '')

        items = []
        for item in data_json.get('items', []):
            price = item.get('price', 0) / 100
            total = item.get('sum', 0) / 100
            quantity = item.get('quantity', 1)
            items.append({
                "name": item.get('name', '').strip(),
                "price": round(price, 2),
                "quantity": quantity,
                "sum": round(total, 2)
            })

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