import pandas as pd
from .utils import normalize_text
from .categorization import get_operation_type, parse_description

class TransactionProcessor:
    def __init__(self, rules: dict):
        self.rules = rules

    def enrich_and_clean(self, raw_records: list) -> pd.DataFrame:
        df = pd.DataFrame(raw_records)
        # Определяем тип операции
        df['operation_type'] = df.apply(
            lambda r: get_operation_type(r['category'], r['description'],
                                         r['amount_sign'], self.rules), axis=1
        )
        # Разделяем приход/расход
        df['income'] = df.apply(lambda r: r['amount'] if r['operation_type'] == 'income' else 0.0, axis=1)
        df['expense'] = df.apply(lambda r: r['amount'] if r['operation_type'] == 'expense' else 0.0, axis=1)
        # Парсинг описания
        parsed = df['description'].apply(parse_description)
        df['shop'] = parsed.apply(lambda x: x['shop'])
        df['transaction_type'] = parsed.apply(lambda x: x['operation_type'])

        # Удаляем технические колонки
        df.drop(columns=['amount_sign', 'amount'], inplace=True, errors='ignore')

        # Нормализация строк
        for col in ['date', 'time', 'category', 'shop', 'transaction_type', 'description']:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(normalize_text)

        # Округление чисел
        for col in ['income', 'expense', 'balance']:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

        # Дедупликация
        df = df.drop_duplicates()
        key_cols = ['date', 'time', 'category', 'income', 'expense', 'shop', 'transaction_type']
        if all(c in df.columns for c in key_cols):
            df = df.drop_duplicates(subset=key_cols, keep='first')

        # Сортировка по дате и времени
        df['_datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                         format='%d.%m.%Y %H:%M', errors='coerce')
        df.sort_values('_datetime', inplace=True)
        df.drop(columns=['_datetime'], inplace=True)

        return df[['date', 'time', 'category', 'income', 'expense', 'balance',
                   'shop', 'transaction_type', 'description']]