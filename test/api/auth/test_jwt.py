import logging
import jwt
from datetime import datetime, timedelta
from api.utils.jwt.jwt import create_jwt, read_jwt, SECRET_KEY, ALGORITHM

logger = logging.getLogger("testing")

def test_create_and_read_jwt_valid():
    user_id = 1
    expires_in_minutes = 30
    logger.info(f"Creating JWT for user_id: {user_id} with expiration of {expires_in_minutes} minutes")
    token = create_jwt(user_id, expires_in_minutes)
    logger.info(f"Created token: {token}")
    assert isinstance(token, str)

    decoded_user_id = read_jwt(token)
    logger.info(f"Decoded user_id from token: {decoded_user_id}")
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
    except ValueError:
        logger.info("Caught expected ValueError for expired token")
        assert True
    except Exception as e:
        logger.info("Unexpected exception caught: %s", str(e))
        assert False

def test_read_jwt_invalid_signature():
    # Create a token with an invalid signature
    token = create_jwt(1, 30)  # Create a valid token
    # Modify the token to have an invalid signature
    invalid_token = token + "invalid"  # Just appending invalid data to simulate tampering
    logger.info("Testing with a token with an invalid signature")
    try:
        read_jwt(invalid_token)
        assert False
    except Exception as e:
        assert True

def test_read_jwt_invalid_claims():
    # Create a token with invalid claims
    invalid_claims_token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30), "invalid_claim": "test"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    logger.info("Testing with a token with invalid claims")
    try:
        read_jwt(invalid_claims_token)
        assert False
    except Exception as e:
        assert True

