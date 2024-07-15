import logging
import pytest
import jwt
from datetime import datetime, timedelta
from api.utils.jwt import create_jwt, read_jwt, SECRET_KEY, ALGORITHM

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_create_and_read_jwt_valid():
    user_id = "test_user"
    expires_in_minutes = 30
    logger.info("Creating JWT for user_id: %s with expiration of %d minutes", user_id, expires_in_minutes)
    token = create_jwt(user_id, expires_in_minutes)
    logger.debug("Created token: %s", token)
    assert isinstance(token, str)

    decoded_user_id = read_jwt(token)
    logger.info("Decoded user_id from token: %s", decoded_user_id)
    assert decoded_user_id == user_id

def test_read_jwt_expired():
    # Create a token that expired in the past
    expired_token = jwt.encode(
        {"exp": datetime.utcnow() - timedelta(minutes=1), "sub": "test_user"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    logger.info("Testing with an expired token")
    try:
        read_jwt(expired_token)
    except ValueError as e:
        logger.error("Caught expected ValueError: %s", str(e))
        assert str(e) == "Token has expired"
    else:
        logger.error("ValueError was not raised for expired token")
        assert False
