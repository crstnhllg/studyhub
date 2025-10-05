from tests.conftest import client, test_user, test_group



def test_get_user_profile(test_user):
    response =  client.get('/users/me')
    data = response.json()
    email, username = data.get('email'), data.get('username')

    assert response.status_code == 200
    assert email == test_user.email
    assert username == test_user.username


def test_get_user_memberships(test_group, test_user):
    response = client.get('/users/me/memberships')
    data = response.json()

    assert response.status_code == 200
    assert any(membership.get('user_id') == test_user.id for membership in data)
    assert any(membership.get('group_id') == test_group.id for membership in data)


def test_update_user_email(test_user):
    request_data = {
        'new_email': 'new_email@email.com',
        'password': '12345'
    }
    response = client.put('/users/email', json=request_data)
    data = response.json()

    assert response.status_code == 200
    assert data.get('id') == test_user.id
    assert data.get('email') == request_data.get('new_email')
    assert data.get('username') == test_user.username


def test_update_user_password():
    request_data = {
        'old_password': '12345',
        'new_password': '54321'
    }
    response = client.put('/users/password', json=request_data)

    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'Password updated successfully'
    }


def test_delete_account():
    request_data = {
        'password': '12345'
    }
    response = client.request('DELETE', '/users/me', json=request_data)

    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'Account deleted successfully'
    }


def test_delete_account_invalid_password():
    request_data = {
        'password': 'invalid_password'
    }
    response = client.request('DELETE', '/users/me', json=request_data)

    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid password'}
