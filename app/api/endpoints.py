"""
Маршруты (эндпоинты) FastAPI:
- /pdftocsv_json/ – конвертация PDF в CSV с категоризацией
- /check/         – получение данных чека через внешний API
"""
import base64
import tempfile
import os
import time
from fastapi import APIRouter, HTTPException
from .models import PDFRequest, CheckInput
from ..core.parser import PDFTransactionReader          # чтение таблиц из PDF
from ..core.transactions import TransactionProcessor   # обработка транзакций
from ..core.rules import RuleLoader                   # загрузка правил категоризации
from ..services.check_service import CheckService     # работа с API проверки чеков

router = APIRouter()
rules_loader = RuleLoader()   # один экземпляр для загрузки правил

def safe_remove_file(filepath: str, max_attempts: int = 5, delay: float = 0.2):
    """
    Безопасное удаление временного файла.
    Пытается удалить несколько раз, т.к. Windows может блокировать файл после записи.
    """
    for attempt in range(max_attempts):
        try:
            os.unlink(filepath)
            return
        except PermissionError:
            if attempt == max_attempts - 1:
                pass  # после последней попытки сдаёмся (можно залогировать)
            else:
                time.sleep(delay)
        except FileNotFoundError:
            return  # файл уже удалён – всё в порядке

@router.post("/pdftocsv_json/")
async def convert_pdf_to_csv_json(request: PDFRequest):
    """
    Принимает PDF в base64, сохраняет во временный файл,
    извлекает транзакции, категоризирует и возвращает CSV.
    """
    # Декодируем base64 в байты
    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Некорректные данные base64")

    tmp_path = None
    try:
        # Создаём временный PDF-файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        # Читаем транзакции из PDF
        reader = PDFTransactionReader(tmp_path)
        raw_data = reader.parse_transactions()

        # Обогащаем, нормализуем, удаляем дубли и сортируем
        processor = TransactionProcessor(rules_loader.load())
        df = processor.enrich_and_clean(raw_data)

        # Преобразуем DataFrame в CSV (с разделителем ';' и кодировкой UTF-8 с BOM)
        csv_string = df.to_csv(index=False, sep=';', quotechar='"', quoting=1, encoding='utf-8-sig')
        return {"csv": csv_string}

    except ValueError as ve:
        # Ошибки, связанные с некорректными данными (например, нет таблиц)
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        # Все остальные ошибки – внутренняя ошибка сервера
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    finally:
        # Гарантированно удаляем временный файл
        if tmp_path and os.path.exists(tmp_path):
            safe_remove_file(tmp_path)

@router.post("/check/")
async def read_check(request: CheckInput):
    """
    Отправляет QR-код во внешний API проверки чеков и возвращает структурированные данные.
    """
    service = CheckService()
    try:
        result = service.get_check_data(request.token, request.qrraw)
        return result
    except ValueError as e:
        # Ошибка от API (неверный QR, лимит и т.п.)
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        # Проблемы сети или недоступность API
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        # Неизвестная ошибка
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")