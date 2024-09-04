from api.sessions.email import BaseEmailAccess


def invite(to: str, code: str, invite_id: str, groupid: str, email_access: BaseEmailAccess) -> bool:
    return email_access.send(to, "TRITT UNSERER GRUPPE BEI", f"Hier der link zu unserer gruppe. http://localhost:8000/group/{invite_id}/{code}/{groupid}")

    