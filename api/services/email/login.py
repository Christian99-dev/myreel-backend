from api.config.email_access import BaseEmailAccess


def login(to: str, code: str, email_access: BaseEmailAccess):
    email_access.send(to, "LOGIN REQUEST", f"Dein Logincode ist {code}")
    