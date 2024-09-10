from api.sessions.email import BaseEmailSessionManager


def login(to: str, code: str, email_session: BaseEmailSessionManager) -> bool:
    return email_session.send(to, "LOGIN REQUEST", f"Dein Logincode ist {code}")
    