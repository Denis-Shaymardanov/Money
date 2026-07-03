"""
Модели данных, используемые для валидации входящих запросов.
"""
from pydantic import BaseModel

class PDFRequest(BaseModel):
    """Запрос на конвертацию PDF в CSV."""
    pdf_base64: str     # PDF-файл, закодированный в base64

class CheckInput(BaseModel):
    """Запрос на получение данных чека по QR-коду."""
    token: str          # API-токен сервиса проверки чеков
    qrraw: str          # сырая строка QR-кода