import os
from datetime import datetime, timedelta

import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def create_jwt(user_id: int, expires_in_minutes: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    to_encode = {"exp": expire, "sub": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def read_jwt(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("User ID not found in token")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:  # Use PyJWTError for general JWT errors
        raise ValueError("Token is invalid")
