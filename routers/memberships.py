from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.user import CurrentUserResponse, MessageResponse
from schemas.membership import MembershipResponse, MemberUpdateRequest
from core.security import get_current_user
from models import StudyGroup, Membership
from starlette import status
from typing import Annotated, List
from database import get_db
from sqlalchemy.orm import Session, joinedload
from core.utils import require_role, get_group_member


router = APIRouter(
    prefix='/study-groups',
    tags=['Study Groups']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[CurrentUserResponse, Depends(get_current_user)]


def authorize_role_update(member_role: str, target_role: str, requested_role: str) -> None:
    require_role(member_role, ['Admin', 'Creator'])

    if member_role != 'Creator' and requested_role == 'Creator':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only the Creator can transfer ownership.'
        )

    if member_role == 'Admin' and target_role == 'Admin' and requested_role != 'Admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only the Creator can demote an Admin.'
        )


@router.get('/{group_id}/members', status_code=status.HTTP_200_OK, response_model=List[MembershipResponse])
async def get_members(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):

    get_group_member(db, user, group_id)

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
async def join_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):

    if not db.get(StudyGroup, group_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found.')

    if db.query(Membership).filter(
            Membership.user_id == user.user_id,
            Membership.group_id == group_id
    ).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are already a member of this group!')

    new_member = Membership(
        user_id=user.user_id,
        group_id=group_id
    )

    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    return MessageResponse(
        success=True,
        message='Successfully joined the group.'
    )


@router.put('/{group_id}/member/{user_id}', status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def update_member_role(
        db: db_dependency,
        user: user_dependency,
        member_request: MemberUpdateRequest,
        group_id: int = Path(gt=0),
        user_id: int = Path(gt=0)
):
    acting_member = get_group_member(db, user, group_id)

    target_member = db.query(Membership).filter(
        Membership.user_id == user_id,
        Membership.group_id == group_id
    ).first()

    if not target_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Member not found in this group.')

    authorize_role_update(acting_member.role, target_member.role, member_request.role)

    target_member.role = member_request.role
    db.commit()
    db.refresh(target_member)

    return MessageResponse(
        success=True,
        message='Successfully updated member role.'
    )


@router.delete('/{group_id}/leave', status_code=status.HTTP_204_NO_CONTENT)
async def leave_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):

    member = get_group_member(db, user, group_id)

    if member.role == 'Creator':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Must transfer ownership first.')

    db.delete(member)
    db.commit()
