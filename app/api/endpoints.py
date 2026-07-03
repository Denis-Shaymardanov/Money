import base64
import tempfile
import os
import time
from fastapi import APIRouter, HTTPException
from .models import PDFRequest, CheckInput
from ..core.parser import PDFTransactionReader
from ..core.transactions import TransactionProcessor
from ..core.rules import RuleLoader
from ..services.check_service import CheckService

router = APIRouter()
rules_loader = RuleLoader()

def safe_remove_file(filepath: str, max_attempts: int = 5, delay: float = 0.2):
    """Пытается удалить файл несколько раз, если он занят."""
    for attempt in range(max_attempts):
        try:
            os.unlink(filepath)
            return
        except PermissionError:
            if attempt == max_attempts - 1:
                # Если после всех попыток не удалось — просто логируем (в будущем можно добавить логгер)
                pass
            else:
                time.sleep(delay)
        except FileNotFoundError:
            return

@router.post("/pdftocsv_json/")
async def convert_pdf_to_csv_json(request: PDFRequest):
    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)
    except Exception:
        raise HTTPException(status_code=400, detail="Некорректные данные base64")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        reader = PDFTransactionReader(tmp_path)
        raw_data = reader.parse_transactions()

        processor = TransactionProcessor(rules_loader.load())
        df = processor.enrich_and_clean(raw_data)

        csv_string = df.to_csv(index=False, sep=';', quotechar='"', quoting=1, encoding='utf-8-sig')
        return {"csv": csv_string}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            safe_remove_file(tmp_path)

@router.post("/check/")
async def read_check(request: CheckInput):
    service = CheckService()
    try:
        result = service.get_check_data(request.token, request.qrraw)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")