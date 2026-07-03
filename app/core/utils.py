"""
Вспомогательные утилиты: нормализация строк и очистка чисел.
"""
import re
import unicodedata
import pandas as pd

def normalize_text(text: str) -> str:
    """
    Приводит строку к единому виду:
    - удаляет невидимые управляющие символы
    - заменяет все виды пробелов на обычный пробел
    - убирает повторяющиеся пробелы
    - переводит в нижний регистр
    Возвращает пустую строку, если на входе NaN.
    """
    if pd.isna(text):
        return ''
    s = str(text)
    s = unicodedata.normalize('NFKC', s)                       # Unicode-нормализация
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)    # удаляем управляющие символы
    s = re.sub(r'[ \t\n\r\f\v\u00a0\u2000-\u200f\u2028-\u202f]', ' ', s)  # все пробельные → обычный пробел
    s = re.sub(r'\s+', ' ', s)                                 # несколько пробелов подряд → один
    return s.strip().lower()

def clean_number(s, keep_sign=False):
    """
    Очищает строку с числом:
    - удаляет пробелы
    - заменяет запятую на точку
    - умеет обрабатывать знак '+' (опционально)
    Возвращает:
        если keep_sign=False: число float или None при ошибке
        если keep_sign=True : кортеж (знак, число) или (None, None)
    """
    if pd.isna(s):
        return (None, None) if keep_sign else None
    s = str(s).strip()
    sign = ''
    if keep_sign and s.startswith('+'):
        sign = '+'
        s = s[1:].strip()
    s = re.sub(r'\s+', '', s).replace(',', '.')   # убираем пробелы, запятую → точку
    try:
        num = float(s)
        return (sign, num) if keep_sign else num
    except ValueError:
        return (None, None) if keep_sign else None