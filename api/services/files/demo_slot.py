from api.sessions.files import BaseFileSessionManager


def get(media_access: BaseFileSessionManager) -> bytes:
    return media_access.get("demo.mp4", "demo_slot")