from tests.conftest import client, test_user, test_group
from app.models import StudyGroup, Membership



def test_get_members(test_user, test_group):
    response = client.get(f'/study-groups/{test_group.id}/members')
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert any(member.get('user_id') == test_user.id for member in data)
    assert any(member.get('username') == test_user.username for member in data)


def test_join_group(db_session, test_user):
    new_group = StudyGroup(
        name='New Group',
        description='New description',
        owner_id=test_user.id
    )
    db_session.add(new_group)
    db_session.commit()

    response = client.post(f'/study-groups/{new_group.id}/join')
    assert response.status_code == 201
    assert response.json() == {
        'success': True,
        'message': 'Successfully joined the study group'
    }

    membership = db_session.query(Membership).filter(
        Membership.group_id == new_group.id,
        Membership.user_id == test_user.id
    ).first()
    assert membership is not None


def test_update_member_role(db_session, test_group, test_member):
    request_data = {
        'role': 'Admin'
    }
    response = client.put(f'/study-groups/{test_group.id}/member/{test_member.id}', json=request_data)
    data = response.json()
    user_id, group_id, role = data.get('user_id'), data.get('group_id'), data.get('role')
    db_session.refresh(test_member)

    assert response.status_code == 200
    assert user_id == test_member.id
    assert group_id == test_group.id
    assert role == request_data.get('role')


def test_leave_group(db_session, test_user, test_group):
    # Temporarily change owner role to member so they can leave the group
    membership = db_session.query(Membership).filter(
        Membership.user_id == test_user.id,
        Membership.group_id == test_group.id
    ).first()
    membership.role = 'Member'

    db_session.commit()

    response = client.delete(f'/study-groups/{test_group.id}/leave')
    assert response.status_code == 200
    assert response.json() == {
        'success': True,
        'message': 'Successfully left the study group'
    }

    membership_check = db_session.query(Membership).filter(
        Membership.user_id == test_user.id,
        Membership.group_id == test_group.id
    ).first()
    assert membership_check is None

