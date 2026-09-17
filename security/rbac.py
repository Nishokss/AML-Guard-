from config.roles import Role, customer_in_scope, has_permission
from security.pii_masking import mask_record

def access(role: str, permission: str) -> bool:
    return has_permission(role, permission)

def protect_customer_record(role: str, record: dict) -> tuple[bool, dict | None]:
    if not customer_in_scope(role, record.get("customer_id", "")):
        return False, None
    if access(role, "customer_pii"):
        return True, dict(record)
    if access(role, "masked_customer"):
        return True, mask_record(record)
    return False, None
