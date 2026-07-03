# Money – Сервис парсинга чеков и конвертации банковских PDF в CSV

Сервер на FastAPI, который принимает PDF-выписку банка в base64 и возвращает CSV с транзакциями, а также получает данные чека по QR-коду через API «Проверка чека».

## Требования
- Python 3.10+
- Установленный Ghostscript (нужен для camelot-py)
- Зависимости из `requirements.txt`

## Установка
cd Money
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt

## Запуск
python main.py
Сервер запустится на http://127.0.0.1:8000. Логи пишутся в server.log.

## API

### POST /pdftocsv_json/
Конвертирует PDF-выписку в CSV.

Тело запроса:

json
{
  "pdf_base64": "строка файла в base64"
}

Ответ:
json
{
  "csv": "Дата;Время;Категория;Приход;Расход;Остаток;Магазин;ТипТранзакции;Описание\n..."
}

### POST /check/
Получает данные чека по QR-коду.
Тело запроса:

json
{
  "token": "ваш_токен",
  "qrraw": "сырая строка QR-кода"
}
Ответ:

json
{
  "shop": {"name": "Магазин", "legal_name": "ООО Ромашка"},
  "items": [{"name": "Товар", "price": 100.00, "quantity": 1, "sum": 100.00}],
  "total_sum": 100.00,
  "datetime": "2023-10-01T12:00:00"
}

## Структура проекта

Money/
├── main.py # точка входа
├── requirements.txt
├── rules.json # правила категоризации
├── app/
│ ├── init.py # создание FastAPI
│ ├── api/
│ │ ├── endpoints.py # маршруты
│ │ └── models.py # модели
│ ├── core/
│ │ ├── parser.py # чтение PDF
│ │ ├── transactions.py # обработка транзакций
│ │ ├── categorization.py
│ │ ├── rules.py
│ │ └── utils.py
│ └── services/
│ └── check_service.py # API чеков
└── AccountingOfGoods/ # конфигурация 1С

## Настройка правил
Файл rules.json содержит списки ключевых слов для определения доходов и переводов. Изменения вступают в силу после перезапуска сервера.