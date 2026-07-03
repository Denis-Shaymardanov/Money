"""
Загрузка правил категоризации из файла rules.json.
Если файл отсутствует – используются значения по умолчанию.
"""
import json
import os
from typing import Dict, Any

class RuleLoader:
    def __init__(self, rules_path: str = "rules.json"):
        self.rules_path = rules_path
        self.rules = self._load_defaults()   # начинаем с правил по умолчанию

    def load(self) -> Dict[str, Any]:
        """Загружает правила из JSON-файла, если он существует."""
        if not os.path.exists(self.rules_path):
            print(f"Файл правил {self.rules_path} не найден, используются настройки по умолчанию")
            return self.rules
        try:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.rules = json.load(f)
            print("Правила загружены")
        except Exception as e:
            print(f"Ошибка загрузки правил: {e}")
        return self.rules

    def reload(self):
        """Принудительно перезагрузить правила (может пригодиться для горячей замены)."""
        return self.load()

    @staticmethod
    def _load_defaults():
        """Правила по умолчанию, если файл не найден."""
        return {
            "income_keywords": [
                "заработная плата", "аванс", "поступление", "возврат",
                "перевод от", "зачисление"
            ],
            "transfer_keywords": [
                "перевод с карты", "перевод на карту", "KARTA-VKLAD",
                "VKLAD-KARTA", "сбп между своими"
            ],
            "category_mapping": {}
        }