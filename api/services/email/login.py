from api.sessions.email import BaseEmailAccess


def login(to: str, code: str, email_access: BaseEmailAccess) -> bool:
    return email_access.send(to, "LOGIN REQUEST", f"Dein Logincode ist {code}")
    