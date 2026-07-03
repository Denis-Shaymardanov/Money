"""
Чтение PDF-файла с помощью библиотеки camelot и извлечение сырых записей транзакций.
"""
import re
import pandas as pd
import camelot
from .utils import clean_number

class PDFTransactionReader:
    """Читает PDF, извлекает таблицы и возвращает список словарей с транзакциями."""

    def __init__(self, pdf_path: str, pages='all', flavor='stream'):
        """
        pdf_path: путь к PDF-файлу
        pages:   страницы для обработки ('all' – все)
        flavor:  метод парсинга camelot ('stream' или 'lattice')
        """
        self.pdf_path = pdf_path
        self.pages = pages
        self.flavor = flavor

    def extract_raw_table(self) -> pd.DataFrame:
        """
        Извлекает все таблицы из PDF с помощью camelot и объединяет их.
        Ожидаются таблицы ровно с 5 колонками.
        """
        tables = camelot.read_pdf(self.pdf_path, pages=self.pages, flavor=self.flavor)
        valid = [t.df for t in tables if t.df.shape[1] == 5]   # только 5-колоночные
        if not valid:
            raise ValueError("Не найдено таблиц с 5 колонками")
        return pd.concat(valid, ignore_index=True)

    @staticmethod
    def find_amount_column(df: pd.DataFrame) -> int:
        """
        Ищет колонку, в которой находятся денежные суммы.
        Анализирует первые 50 значений: если большинство выглядят как сумма (число с двумя знаками после запятой),
        считаем, что это колонка с суммой.
        Если не найдено – возвращает колонку 3 (эмпирическое предположение).
        """
        def is_amount_cell(x):
            if not isinstance(x, str):
                return False
            cleaned = re.sub(r'\s+', '', x).lstrip('+')
            return bool(re.match(r'^\d+[,.]\d{2}$', cleaned))
        for col in df.columns:
            sample = df[col].dropna().astype(str).head(50)
            if sample.apply(is_amount_cell).sum() > 5:
                return col
        return 3

    @staticmethod
    def is_transaction_row(row: pd.Series, amount_col: int) -> bool:
        """
        Проверяет, является ли строка DataFrame строкой с транзакцией.
        Условия:
        - первая ячейка содержит дату в формате ДД.ММ.ГГГГ
        - вторая ячейка содержит время ЧЧ:ММ
        - колонка с суммой не пуста
        """
        if not re.match(r'\d{2}\.\d{2}\.\d{4}', str(row[0]).strip()):
            return False
        if not re.match(r'\d{2}:\d{2}', str(row[1]).strip()):
            return False
        val = row[amount_col]
        if pd.isna(val) or str(val).strip() == '':
            return False
        return True

    def parse_transactions(self) -> list:
        """
        Основной метод: извлекает таблицы, находит колонку суммы,
        итерируется по строкам-транзакциям и собирает сырые данные в список словарей.
        """
        df = self.extract_raw_table()
        amount_col = self.find_amount_column(df)
        balance_col = amount_col + 1 if amount_col + 1 in df.columns else amount_col

        # Индексы строк, начинающих транзакцию
        indices = df[df.apply(lambda row: self.is_transaction_row(row, amount_col), axis=1)].index
        records = []

        for idx in indices:
            row_op = df.loc[idx]
            sign, amount = clean_number(row_op[amount_col], keep_sign=True)
            if amount is None:
                continue
            balance = clean_number(row_op[balance_col])

            # Собираем строки описания, следующие за строкой транзакции
            desc_lines = []
            next_idx = idx + 1
            while next_idx < len(df) and not self.is_transaction_row(df.loc[next_idx], amount_col):
                code = str(df.loc[next_idx, 1]) if pd.notna(df.loc[next_idx, 1]) else ''
                desc = str(df.loc[next_idx, 2]) if pd.notna(df.loc[next_idx, 2]) else ''
                line = f"{code} {desc}".strip()
                if line:
                    desc_lines.append(line)
                next_idx += 1

            records.append({
                'date': str(row_op[0]).strip(),
                'time': str(row_op[1]).strip(),
                'category': str(row_op[2]).strip(),
                'amount_sign': sign,
                'amount': amount,
                'balance': balance,
                'description': ' | '.join(desc_lines)
            })
        return records