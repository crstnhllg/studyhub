from models import StudyGroup, Membership
from sqlalchemy.orm import Session
from fastapi import HTTPException
from starlette import status


def get_group_member(db: Session, user, group_id: int):
    member = db.query(Membership).filter(
        Membership.user_id == user.user_id,
        Membership.group_id == group_id).first()

    if not member:
        if not db.get(StudyGroup, group_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Group not found.'
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be a group member to perform this action.'
        )
    return member


def require_role(member_role, allowed_roles: list[str]):

    if member_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'You must have one of these roles: {allowed_roles}.'
        )
