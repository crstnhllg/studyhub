from tests.conftest import client, test_group, test_subject
from app.models import Subject



def test_get_subjects(test_subject, test_group):
    response = client.get(f'/subjects/{test_group.id}')
    data = response.json()

    assert response.status_code == 200
    assert any(subject.get('id') == test_subject.id for subject in data)
    assert any(subject.get('name') == test_subject.name for subject in data)
    assert any(subject.get('group_id') == test_group.id for subject in data)


def test_create_subject(test_group):
    request_data = {
        'name': 'New Subject'
    }
    response = client.post(f'/subjects/{test_group.id}', json=request_data)
    data = response.json()
    name, group_id = data.get('name'), data.get('group_id')

    assert response.status_code == 201
    assert name == request_data.get('name')
    assert group_id == test_group.id


def test_update_subject(db_session, test_group, test_subject):
    request_data = {
        'name': 'Updated Subject'
    }
    response = client.put(f'/subjects/{test_group.id}/{test_subject.id}', json=request_data)
    data = response.json()
    id_, name, group_id = data.get('id'), data.get('name'), data.get('group_id')
    db_session.refresh(test_subject)

    assert response.status_code == 200
    assert id_ == test_subject.id
    assert name == request_data.get('name')
    assert group_id == test_group.id


def test_delete_subject(db_session, test_group, test_subject):
    response = client.delete(f'/subjects/{test_group.id}/{test_subject.id}')
    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message':'Subject deleted successfully'
    }

    subject = db_session.query(Subject).filter(Subject.id == test_subject.id).first()
    assert subject is None


