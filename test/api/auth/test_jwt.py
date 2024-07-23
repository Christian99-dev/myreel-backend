import logging
import jwt
from datetime import datetime, timedelta
from api.auth.jwt import create_jwt, read_jwt, SECRET_KEY, ALGORITHM

logger = logging.getLogger("testing")

def test_create_and_read_jwt_valid():
    user_id = 1
    expires_in_minutes = 30
    logger.info(f"Creating JWT for user_id: {user_id} with expiration of  {expires_in_minutes} minutes")
    token = create_jwt(user_id, expires_in_minutes)
    logger.info("Created token: {token}")
    assert isinstance(token, str)

    decoded_user_id = read_jwt(token)
    logger.info("Decoded user_id from token: {decoded_user_id}")
    assert isinstance(decoded_user_id, int)
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
        logger.info("Caught expected ValueError: %s", str(e))
        assert str(e) == "Token has expired"
    else:
        logger.info("ValueError was not raised for expired token")
        assert False
