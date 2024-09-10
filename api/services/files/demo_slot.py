from api.sessions.files import BaseFileSessionManager


def get(file_session: BaseFileSessionManager) -> bytes:
    return file_session.get("demo.mp4", "demo_slot")