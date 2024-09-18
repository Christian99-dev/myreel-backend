from api.sessions.files import BaseFileSessionManager

def get(file_session: BaseFileSessionManager) -> bytes:
    return file_session.get("demo", "demo_slot")