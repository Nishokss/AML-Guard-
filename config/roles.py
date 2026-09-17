from enum import Enum

class Role(str, Enum):
    ADMIN = "ADMIN"
    AML_ANALYST = "AML_ANALYST"
    EXTERNAL_AUDITOR = "EXTERNAL_AUDITOR"
    RELATIONSHIP_MANAGER = "RELATIONSHIP_MANAGER"

PERMISSIONS = {
    Role.ADMIN: {"transactions", "alerts", "customer_pii", "regulations", "sanctions", "audit_logs", "decisions"},
    Role.AML_ANALYST: {"transactions", "alerts", "regulations", "sanctions", "masked_customer", "decisions"},
    Role.EXTERNAL_AUDITOR: {"audit_logs", "decisions", "regulations"},
    Role.RELATIONSHIP_MANAGER: {"transactions", "alerts", "regulations", "masked_customer", "decisions"},
}

# Demo portfolio scope for the additional restricted role. In production this
# would come from an entitlement service or an effective-dated database table.
PORTFOLIO_CUSTOMERS = {
    Role.RELATIONSHIP_MANAGER: {f"C{number:03d}" for number in range(1, 11)},
}

def has_permission(role: str | Role, permission: str) -> bool:
    try:
        role = Role(role)
    except ValueError:
        return False
    return permission in PERMISSIONS.get(role, set())

def customer_in_scope(role: str | Role, customer_id: str) -> bool:
    try:
        role = Role(role)
    except ValueError:
        return False
    allowed_customers = PORTFOLIO_CUSTOMERS.get(role)
    return allowed_customers is None or customer_id in allowed_customers

def scoped_customers(role: str | Role) -> set[str] | None:
    try:
        role = Role(role)
    except ValueError:
        return set()
    return PORTFOLIO_CUSTOMERS.get(role)
