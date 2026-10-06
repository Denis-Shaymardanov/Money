from app.core.transactions import TransactionProcessor


def record(description, amount_sign="-", amount=100.0):
    return {
        "date": "05.10.2026",
        "time": "12:30",
        "category": "Покупка",
        "amount_sign": amount_sign,
        "amount": amount,
        "balance": 1000.0,
        "description": description,
    }


def test_identical_operations_are_not_removed_inside_one_statement():
    processor = TransactionProcessor({})

    result = processor.enrich_and_clean([
        record("123456 Магазин X | Операция по карте ****1234"),
        record("123456 Магазин X | Операция по карте ****1234"),
    ])

    assert len(result) == 2


def test_same_authorization_code_does_not_merge_refund_and_debit():
    processor = TransactionProcessor({})

    result = processor.enrich_and_clean([
        record("089375 Возврат | Операция по карте ****1234", "+", 11.0),
        record("089375 Списание | Операция по карте ****1234", "-", 11.0),
    ])

    assert len(result) == 2
    assert result["income"].tolist() == [11.0, 0.0]
    assert result["expense"].tolist() == [0.0, 11.0]


def test_repeated_import_is_not_decided_by_python_layer():
    processor = TransactionProcessor({})
    operation = record("123456 Магазин X | Операция по карте ****1234")

    result = processor.enrich_and_clean([operation, operation.copy()])

    # Both rows reach 1C, where the persistent operation matcher decides
    # whether this is a repeat import or two real operations.
    assert len(result) == 2
