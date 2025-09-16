from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func
from schemas.user import CurrentUserResponse
from schemas.study_group import GroupRequest, GroupResponse
from core.security import get_current_user
from core.utils import get_group_member, require_role
from models import StudyGroup, Membership
from starlette import status
from typing import Annotated, List
from database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix='/study-groups',
    tags=['Study Groups']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[CurrentUserResponse, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK, response_model=List[GroupResponse])
async def get_groups(db: db_dependency):
    return db.query(StudyGroup).all()


@router.get('/{group_id}', status_code=status.HTTP_200_OK, response_model=GroupResponse)
async def get_group_by_id(db: db_dependency, group_id: int = Path(gt=0)):

    group = db.get(StudyGroup, group_id)
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found!')

    return group


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=GroupResponse)
async def create_group(db: db_dependency, user: user_dependency, group_request: GroupRequest):

    group_exists = db.query(StudyGroup).filter(
        func.lower(StudyGroup.name) == func.lower(group_request.name)
    ).first()

    if group_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Study group name already exists!')

    group = StudyGroup(
        name=group_request.name,
        description=group_request.description,
        owner_id=user.user_id
    )

    db.add(group)
    db.flush()

    creator = Membership(
        user_id=user.user_id,
        group_id=group.id,
        role='Creator'
    )

    db.add(creator)
    db.commit()
    db.refresh(group)

    return group


@router.put('/{group_id}', status_code=status.HTTP_200_OK)
async def update_group(db: db_dependency, user: user_dependency, group_request: GroupRequest, group_id: int):

    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Creator', 'Admin'])

    group_exists = db.query(StudyGroup).filter(
        func.lower(StudyGroup.name) == func.lower(group_request.name),
        StudyGroup.id != group_id
    ).first()

    if group_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Study group name already exists!')

    group = db.get(StudyGroup, group_id)
    group.name = group_request.name
    group.description = group_request.description

    db.commit()
    db.refresh(group)


@router.delete('/{group_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Creator', 'Admin'])

    group = db.get(StudyGroup, group_id)
    db.delete(group)
    db.commit()