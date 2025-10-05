from app.core.utils import validate_role, validate_membership, validate_group, get_membership
from app.schemas.membership import MembershipResponse, MemberUpdateRequest, UpdateRoleResponse
from app.core.constants import ALLOWED_ROLES, CREATOR_ROLE
from fastapi import APIRouter, HTTPException, Path
from app.schemas.common import MessageResponse
from app.dependencies import user_dependency
from app.database import db_dependency
from sqlalchemy.orm import joinedload
from app.models import Membership
from starlette import status
from typing import List



router = APIRouter(
    prefix='/study-groups',
    tags=['Study Groups']
)


@router.get('/{group_id}/members', status_code=status.HTTP_200_OK, response_model=List[MembershipResponse])
def get_members(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Retrieve all members of a specified study group.
    """
    validate_membership(db, user.id, group_id)

    members = db.query(Membership).options(
        joinedload(Membership.user)
    ).filter(Membership.group_id == group_id).all()

    return [
        MembershipResponse(
            user_id=m.user_id,
            username=m.user.username,
            role=m.role
        ) for m in members
    ]


@router.post('/{group_id}/join', status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
def join_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Join a study group by its ID if the user is not already a member.
    """
    validate_group(db, group_id)

    is_member = get_membership(db, user.id, group_id)
    if is_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='You are already a member of this study group'
        )

    new_member = Membership(
        user_id=user.id,
        group_id=group_id
    )
    db.add(new_member)
    db.commit()

    return MessageResponse(
        success=True,
        message='Successfully joined the study group'
    )


@router.put('/{group_id}/member/{user_id}', status_code=status.HTTP_200_OK, response_model=UpdateRoleResponse)
def update_member_role(
        db: db_dependency,
        user: user_dependency,
        member_request: MemberUpdateRequest,
        group_id: int = Path(gt=0),
        user_id: int = Path(gt=0)
):
    """
    Update the role of a specific member in a study group.
    Only group admins or creators can perform this action.
    """
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)

    target_member = get_membership(db, user_id, group_id)
    if target_member is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified member could not be found in this group'
        )

    target_member.role = member_request.role
    db.commit()

    return target_member


@router.delete('/{group_id}/leave', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def leave_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Allow a member to leave a study group.
    The creator cannot leave the group without transferring ownership first.
    """
    membership = validate_membership(db, user.id, group_id)

    if membership.role == CREATOR_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Group creator must transfer ownership before leaving the group'
        )

    db.delete(membership)
    db.commit()

    return MessageResponse(
        success=True,
        message='Successfully left the study group'
    )

