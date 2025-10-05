from app.core.security import create_access_token, get_current_user, ALGORITHM, SECRET_KEY
from tests.conftest import client, test_user, db_session
from datetime import timedelta
from app.models import User
from jose import jwt



def test_create_user():
    request_data = {
        'email': 'new_user@email.com',
        'username': 'new_user',
        'password': '12345'
    }
    response = client.post('/auth/', json=request_data)
    data = response.json()

    assert response.status_code == 201
    assert all(data.get(k) == v for k, v in request_data.items() if k != 'password')


def test_login_for_access_token(test_user):
    request_data = {
        'username': test_user.username,
        'password': '12345'
    }
    response = client.post('/auth/token', data=request_data)
    data = response.json()

    assert response.status_code == 200
    assert 'access_token' in data
    assert data.get('token_type') == 'bearer'


def test_invalid_login():
    request_data = {
        'username': 'invalid_username',
        'password': 'invalid_password'
    }
    response = client.post('/auth/token', data=request_data)
    assert response.status_code == 401


def test_create_and_decode_access_token(test_user):
    access_token = create_access_token(test_user.username, test_user.id, timedelta(minutes=60))
    assert access_token is not None
    assert isinstance(access_token, str)

    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload is not None
    assert payload.get('sub') == test_user.username
    assert payload.get('user_id') == test_user.id


def test_get_current_user_from_token(db_session, test_user):
    access_token = create_access_token(test_user.username, test_user.id, timedelta(minutes=60))
    current_user = get_current_user(db_session, access_token)

    assert isinstance(current_user, User)
    assert current_user.id == test_user.id