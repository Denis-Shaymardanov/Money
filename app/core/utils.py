import re
import unicodedata
import pandas as pd

def normalize_text(text: str) -> str:
    if pd.isna(text):
        return ''
    s = str(text)
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    s = re.sub(r'[ \t\n\r\f\v\u00a0\u2000-\u200f\u2028-\u202f]', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip().lower()

def clean_number(s, keep_sign=False):
    if pd.isna(s):
        return (None, None) if keep_sign else None
    s = str(s).strip()
    sign = ''
    if keep_sign and s.startswith('+'):
        sign = '+'
        s = s[1:].strip()
    s = re.sub(r'\s+', '', s).replace(',', '.')
    try:
        num = float(s)
        return (sign, num) if keep_sign else num
    except ValueError:
        return (None, None) if keep_sign else None