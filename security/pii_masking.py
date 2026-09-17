import re

def mask_name(name: str) -> str:
    return " ".join((part[0] + "*" * max(1, len(part) - 1)) if part else part for part in str(name).split())

def mask_identifier(value: str) -> str:
    value = str(value)
    return "*" * max(0, len(value) - 5) + value[-5:]

def mask_phone(value: str) -> str:
    value = str(value)
    return "*" * max(0, len(value) - 4) + value[-4:]

def mask_record(record: dict) -> dict:
    result = dict(record)
    for key in ("sender_name", "receiver_name", "name"):
        if key in result and result[key] is not None:
            result[key] = mask_name(result[key])
    for key in ("customer_id", "account_number"):
        if key in result and result[key] is not None:
            result[key] = mask_identifier(result[key])
    for key in ("phone", "mobile"):
        if key in result and result[key] is not None:
            result[key] = mask_phone(result[key])
    for key in ("address",):
        if key in result:
            result[key] = "[MASKED]"
    return result
