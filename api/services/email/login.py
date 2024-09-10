from api.sessions.email import BaseEmailSessionManager


def login(to: str, code: str, email_access: BaseEmailSessionManager) -> bool:
    return email_access.send(to, "LOGIN REQUEST", f"Dein Logincode ist {code}")
    