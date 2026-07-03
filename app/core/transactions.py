"""
Обработка сырых транзакций: категоризация, разделение на приход/расход,
нормализация, дедупликация и сортировка.
"""
import pandas as pd
from .utils import normalize_text
from .categorization import get_operation_type, parse_description

class TransactionProcessor:
    """Принимает список сырых записей и возвращает чистый DataFrame."""

    def __init__(self, rules: dict):
        """
        rules – словарь с правилами категоризации, загруженный из RuleLoader.
        """
        self.rules = rules

    def enrich_and_clean(self, raw_records: list) -> pd.DataFrame:
        """
        Главный метод обработки:
        1. Определяет тип операции (доход/расход/перевод)
        2. Раскидывает сумму в колонки 'income' и 'expense'
        3. Парсит описание (магазин, тип транзакции)
        4. Нормализует строки и округляет числа
        5. Удаляет дубликаты (в т.ч. по хэшу ключевых полей)
        6. Сортирует по дате и времени
        """
        df = pd.DataFrame(raw_records)

        # --- 1. Определяем тип операции ---
        df['operation_type'] = df.apply(
            lambda r: get_operation_type(r['category'], r['description'],
                                         r['amount_sign'], self.rules), axis=1
        )

        # --- 2. Разносим суммы ---
        df['income'] = df.apply(lambda r: r['amount'] if r['operation_type'] == 'income' else 0.0, axis=1)
        df['expense'] = df.apply(lambda r: r['amount'] if r['operation_type'] == 'expense' else 0.0, axis=1)

        # --- 3. Парсим описание ---
        parsed = df['description'].apply(parse_description)
        df['shop'] = parsed.apply(lambda x: x['shop'])
        df['transaction_type'] = parsed.apply(lambda x: x['operation_type'])

        # Убираем технические колонки, они больше не нужны
        df.drop(columns=['amount_sign', 'amount'], inplace=True, errors='ignore')

        # --- 4. Нормализация строк ---
        for col in ['date', 'time', 'category', 'shop', 'transaction_type', 'description']:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(normalize_text)

        # Округление чисел до двух знаков
        for col in ['income', 'expense', 'balance']:
            df[col] = pd.to_numeric(df[col], errors='coerce').round(2)

        # --- 5. Дедупликация ---
        # Сначала удаляем полные дубликаты
        df = df.drop_duplicates()

        # Затем удаляем дубликаты по ключевым полям (без описания и остатка)
        key_cols = ['date', 'time', 'category', 'income', 'expense', 'shop', 'transaction_type']
        if all(c in df.columns for c in key_cols):
            df = df.drop_duplicates(subset=key_cols, keep='first')

        # --- 6. Сортировка по дате и времени ---
        df['_datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'],
                                         format='%d.%m.%Y %H:%M', errors='coerce')
        df.sort_values('_datetime', inplace=True)
        df.drop(columns=['_datetime'], inplace=True)

        # Возвращаем только нужные колонки в заданном порядке
        return df[['date', 'time', 'category', 'income', 'expense', 'balance',
                   'shop', 'transaction_type', 'description']]