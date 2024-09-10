from api.sessions.instagram import BaseInstagramSessionManager

def upload(video_bytes: bytes, video_format:str, caption: str, instagram_session: BaseInstagramSessionManager):
    return instagram_session.upload(video_bytes, video_format, caption)