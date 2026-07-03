import re

def get_operation_type(category: str, description: str, amount_sign: str, rules: dict) -> str:
    text = f"{category} {description}".lower()
    for kw in rules.get("income_keywords", []):
        if kw.lower() in text:
            return "income"
    for kw in rules.get("transfer_keywords", []):
        if kw.lower() in text:
            return "transfer"
    if amount_sign == "+":
        return "income"
    return "expense"

def parse_description(desc: str) -> dict:
    result = {"shop": "", "operation_type": ""}
    if not desc or not isinstance(desc, str):
        return result
    desc = desc.strip()
    low_desc = desc.lower()

    if "перевод" in low_desc:
        result["operation_type"] = "Перевод"
        idx = -1
        if "от " in low_desc:
            idx = low_desc.find("от ") + 3
        elif "для " in low_desc:
            idx = low_desc.find("для ") + 4
        if idx > 0:
            tail = desc[idx:]
            markers = ["|", " операция", " описание"]
            end_pos = len(tail)
            for m in markers:
                pos = tail.lower().find(m)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
            raw_shop = tail[:end_pos].strip().rstrip('.')
            result["shop"] = raw_shop
        return result

    if "по карте" in low_desc or "операция по карте" in low_desc:
        result["operation_type"] = "Карта"
        clean_desc = re.sub(r'^\d{6}\s+', '', desc)
        clean_desc = re.sub(r'Операция по карте\s*\*{4}\d{4}\s*\|?', '', clean_desc, flags=re.IGNORECASE)
        clean_desc = clean_desc.strip()
        if " RUS." in clean_desc:
            shop = clean_desc.split(" RUS.")[0].strip()
        elif "|" in clean_desc:
            shop = clean_desc.split("|")[0].strip()
        else:
            shop = clean_desc
        shop = shop.rstrip('.')
        if shop.startswith('.'):
            shop = shop[1:]
        result["shop"] = shop
        return result

    if "по счету" in low_desc:
        result["operation_type"] = "Счёт"
        clean_desc = re.sub(r'^\d{6}\s+', '', desc)
        if "|" in clean_desc:
            shop = clean_desc.split("|")[0].strip()
        else:
            shop = clean_desc.split(".")[0].strip()
        result["shop"] = shop
        return result

    result["operation_type"] = "Иное"
    clean_desc = re.sub(r'^\d{6}\s+', '', desc)
    if " RUS." in clean_desc:
        shop = clean_desc.split(" RUS.")[0].strip()
    elif "|" in clean_desc:
        shop = clean_desc.split("|")[0].strip()
    else:
        shop = clean_desc
    shop = shop.rstrip('.')
    if shop.startswith('.'):
        shop = shop[1:]
    result["shop"] = shop
    return result