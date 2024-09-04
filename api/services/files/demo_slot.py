from api.sessions.files import BaseMediaAccess


def get(media_access: BaseMediaAccess) -> bytes:
    return media_access.get("demo.mp4", "demo_slot")