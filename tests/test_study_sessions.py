from tests.conftest import client, test_group, test_subject



def test_get_session_by_subject(test_subject, test_group, test_session):
    response = client.get(f'/study-sessions/{test_group.id}/{test_subject.id}')
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert any(session.get('id') == test_session.id for session in data)
    assert any(session.get('title') == test_session.title for session in data)
    assert any(session.get('status') == test_session.status for session in data)
    assert any(session.get('subject_id') == test_subject.id for session in data)


def test_get_session_subject_not_found(test_subject, test_group, test_session):
    response = client.get(f'/study-sessions/{test_group.id}/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'The specified subject could not be found'}


def test_create_session(test_group, test_subject):
    request_data = {
        'title': 'New Session',
        'description': 'New session description.',
        'date_time': '2025-10-20 15:00',
        'duration': 90,
        'status': 'Scheduled'
    }
    response = client.post(f'/study-sessions/{test_group.id}/{test_subject.id}', json=request_data)
    data = response.json()

    assert response.status_code == 201
    assert all(data.get(key) == value for key, value in request_data.items() if key != 'date_time')


def test_update_session(db_session, test_session):
    request_data = {
        'title': 'Updated Session',
        'description': 'Updated description.',
        'date_time': '2025-07-20 15:00',
        'duration': 30,
        'status': 'Completed'
    }
    response = client.put(f'/study-sessions/{test_session.id}', json=request_data)
    data = response.json()
    db_session.refresh(test_session)

    assert response.status_code == 200
    assert data.get('id') == test_session.id
    assert all(data.get(key) == value for key, value in request_data.items() if key != 'date_time')




