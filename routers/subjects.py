from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.user import CurrentUserResponse
from schemas.subject import SubjectResponse, SubjectRequest
from core.security import get_current_user
from core.utils import get_group_member, require_role
from models import Subject
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


@router.get('/{group_id}/subjects', status_code=status.HTTP_200_OK, response_model=List[SubjectResponse])
async def get_subjects(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):

    get_group_member(db, user, group_id)

    subjects = db.query(Subject).filter(
        Subject.group_id == group_id
    ).all()

    return subjects


@router.post('/{group_id}/subjects', status_code=status.HTTP_201_CREATED, response_model=SubjectResponse)
async def create_subject(
        db: db_dependency,
        user: user_dependency,
        subject_request: SubjectRequest,
        group_id: int = Path(gt=0),
    ):

    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Admin', 'Creator'])

    if db.query(Subject).filter(
        Subject.name == subject_request.name,
        Subject.group_id == group_id
    ).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Duplicate subject is not allowed.'
        )

    new_subject = Subject(
        name=subject_request.name,
        group_id=group_id
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return new_subject


@router.delete('/{group_id}/subjects/{subject_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
        db: db_dependency,
        user: user_dependency,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):

    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Admin', 'Creator'])

    subject = db.get(Subject, subject_id)

    if subject is None or subject.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subject not found.')

    db.delete(subject)
    db.commit()
