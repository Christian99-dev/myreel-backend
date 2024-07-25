from datetime import datetime, timedelta
from api.models.database.model import LoginRequest
from api.services.database.login import create, delete

def test_create(db_session_filled):
    login_request = create(user_id=1, db=db_session_filled)

    assert login_request.user_id == 1
    assert isinstance(login_request.pin, str)
    assert login_request.created_at <= datetime.now()
    assert login_request.expires_at == login_request.created_at + timedelta(minutes=10)

def test_delete(db_session_filled):
    login_request = create(user_id=1, db=db_session_filled)
    user_id = login_request.user_id

    # Ensure the login request exists
    assert db_session_filled.query(LoginRequest).filter(LoginRequest.user_id == user_id).first() is not None

    # Delete the login request
    delete(user_id=user_id, db=db_session_filled)

    # Ensure the login request no longer exists
    assert db_session_filled.query(LoginRequest).filter(LoginRequest.user_id == user_id).first() is None