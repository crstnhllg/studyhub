from app.schemas.study_group import GroupRequest, GroupResponse, GroupTransferRequest
from app.core.constants import ALLOWED_ROLES, CREATOR_ROLE, ADMIN_ROLE
from app.schemas.common import MessageResponse
from app.models import StudyGroup, Membership
from app.dependencies import user_dependency
from fastapi import APIRouter, Path, HTTPException
from app.database import db_dependency
from starlette import status
from typing import List
from app.core.utils import (
    validate_unique_group_name,
    validate_group,
    validate_membership,
    validate_role,
    get_membership
    )



router = APIRouter(
    prefix='/study-groups',
    tags=['Study Groups']
)


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
def get_groups(db: db_dependency, user: user_dependency):
    """
    Retrieve all study groups.
    """
    return db.query(StudyGroup).all()


@router.get('/{group_id}', status_code=status.HTTP_200_OK, response_model=GroupResponse)
def get_group_by_id(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Retrieve a study group by its ID.
    """
    group = validate_group(db, group_id)
    return group


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
def create_group(db: db_dependency, user: user_dependency, group_request: GroupRequest):
    """
    Create a new study group and assign the authenticated user as the creator.
    """
    validate_unique_group_name(db, group_request.name)

    group = StudyGroup(**group_request.model_dump(), owner_id=user.id)

    db.add(group)
    db.flush()

    creator = Membership(
        user_id=user.id,
        group_id=group.id,
        role=CREATOR_ROLE
    )

    db.add(creator)
    db.commit()
    db.refresh(group)

    return group


@router.put('/{group_id}/transfer', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def transfer_group_ownership(
        db: db_dependency,
        user: user_dependency,
        transfer_request: GroupTransferRequest,
        group_id: int = Path(gt=0)
    ):
    """
    Transfer ownership of a study group from the current creator to another member.

    - The original creator becomes an admin.
    - Only the current creator can perform this action.
    """
    target_group = validate_group(db, group_id)
    original_owner = validate_membership(db, user.id, group_id)
    validate_role(original_owner.role, [CREATOR_ROLE])

    new_owner = get_membership(db, transfer_request.new_owner_id, group_id)
    if new_owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified member could not be found in this group'
        )

    if new_owner.role == CREATOR_ROLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The specified member is already the group creator and cannot be assigned ownership'
        )

    new_owner.role = CREATOR_ROLE
    original_owner.role = ADMIN_ROLE

    db.commit()
    db.refresh(target_group)

    return MessageResponse(
        success=True,
        message='Study group ownership transferred successfully'
    )


@router.put('/{group_id}', status_code=status.HTTP_200_OK, response_model=GroupResponse)
def update_group(db: db_dependency, user: user_dependency, group_request: GroupRequest, group_id: int):
    """
    Update the name (and optionally description) of a study group.
    Only Creator or Admin can perform this action.

    """
    target_group = validate_group(db, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)
    validate_unique_group_name(db, group_request.name, group_id)

    for field, value in group_request.model_dump(exclude_unset=True).items():
        setattr(target_group, field, value)

    db.commit()
    db.refresh(target_group)

    return target_group


@router.delete('/{group_id}', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def delete_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Delete a study group permanently.
    Only Creator or Admin can perform this action.
    """
    target_group = validate_group(db, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)

    db.delete(target_group)
    db.commit()

    return MessageResponse(
        success=True,
        message='Group deleted successfully'
    )
