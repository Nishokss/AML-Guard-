import hashlib
from config.roles import Role

DEMO_USERS = {
    "admin": (hashlib.sha256(b"admin123").hexdigest(), Role.ADMIN.value),
    "analyst": (hashlib.sha256(b"analyst123").hexdigest(), Role.AML_ANALYST.value),
    "auditor": (hashlib.sha256(b"auditor123").hexdigest(), Role.EXTERNAL_AUDITOR.value),
    "relationship_manager": (hashlib.sha256(b"rm123").hexdigest(), Role.RELATIONSHIP_MANAGER.value),
}

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(username: str, password: str) -> dict | None:
    item = DEMO_USERS.get(username.lower())
    if item and item[0] == hash_password(password):
        return {"username": username.lower(), "role": item[1]}
    return None
