from tests.conftest import client, test_user, test_group



def test_get_groups(test_group):
    response = client.get('/study-groups/')
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert any(group.get('id') == test_group.id for group in data)
    assert any(group.get('name') == test_group.name for group in data)
    assert any(group.get('description') == test_group.description for group in data)


def test_get_group_by_id(test_group):
    response = client.get(f'/study-groups/{test_group.id}')
    data = response.json()
    id_, name, description = data.get('id'), data.get('name'), data.get('description')

    assert response.status_code == 200
    assert id_ == test_group.id
    assert name == test_group.name
    assert description == test_group.description


def test_get_group_by_id_not_found():
    response = client.get('/study-groups/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'The specified group could not be found'}


def test_create_group(test_user):
    request_data = {
        'name': 'New Group',
        'description': 'New description.',
    }
    response = client.post('/study-groups/', json=request_data)
    data = response.json()

    assert response.status_code == 201
    assert data.get('owner_id') == test_user.id
    assert all(data.get(k) == v for k, v in request_data.items())


def test_transfer_group_ownership(db_session, test_group, test_member):
    request_data = {
        'new_owner_id': test_member.id
    }
    response = client.put(f'/study-groups/{test_group.id}/transfer', json=request_data)
    data = response.json()

    assert response.status_code == 200
    assert data == {
        'success': True,
        'message': 'Study group ownership transferred successfully'
    }


def test_transfer_group_ownership_member_not_found(test_group):
    request_data = {
        'new_owner_id': 1000
    }
    response = client.put(f'/study-groups/{test_group.id}/transfer', json=request_data)
    data = response.json()

    assert response.status_code == 404
    assert data == {'detail': 'The specified member could not be found in this group'}


def test_update_group(test_group):
    request_data = {
        'name': 'Updated Name',
        'description': '',
    }
    response = client.put(f'/study-groups/{test_group.id}', json=request_data)
    data = response.json()
    id_, name, description = data.get('id'), data.get('name'), data.get('description')


    assert response.status_code == 200
    assert id_ == test_group.id
    assert name == request_data.get('name')
    assert description == request_data.get('description')


def test_delete_group(test_group):
    response = client.delete(f'/study-groups/{test_group.id}')

    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'Group deleted successfully'
    }

