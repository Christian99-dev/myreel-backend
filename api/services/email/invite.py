from api.sessions.email import BaseEmailSessionManager


def invite(to: str, code: str, invite_id: str, groupid: str, email_session: BaseEmailSessionManager) -> bool:
    return email_session.send(to, "TRITT UNSERER GRUPPE BEI", f"Hier der link zu unserer gruppe. http://localhost:3000/{groupid}/{invite_id}/{code}")

    