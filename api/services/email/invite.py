from api.config.email_access import BaseEmailAccess


def invite(to: str, code: str, email_access: BaseEmailAccess):
    email_access.send(to, "TRITT UNSERER GRUPPE BEI", f"Dein Invitecode ist {code}")

    