from fastapi import APIRouter, Depends, HTTPException, Path
from schemas.user import CurrentUserResponse
from schemas.study_session import SessionResponse, SessionRequest, SessionUpdateRequest
from core.security import get_current_user
from core.utils import get_group_member, require_role
from models import Subject, StudySession
from starlette import status
from typing import Annotated, List
from database import get_db
from sqlalchemy.orm import Session, joinedload


router = APIRouter(
    prefix='/study-groups',
    tags=['Study Groups']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[CurrentUserResponse, Depends(get_current_user)]


@router.get(
    '/{group_id}/study_sessions/{subject_id}',
    status_code=status.HTTP_200_OK,
    response_model=List[SessionResponse]
    )
async def get_sessions_by_subject(
        db: db_dependency,
        user: user_dependency,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):

    get_group_member(db, user, group_id)

    subject = db.get(Subject, subject_id)
    if not subject or subject.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subject not found!')

    sessions = db.query(StudySession).options(
        joinedload(StudySession.subject)
    ).filter(StudySession.subject_id == subject_id).all()

    return [
        SessionResponse(
            title=s.title,
            description=s.description,
            date_time=s.date_time,
            duration=s.duration,
            status=s.status,
            subject=s.subject.name
        ) for s in sessions
    ]


@router.post(
    '/{group_id}/study_sessions/{subject_id}',
    status_code=status.HTTP_201_CREATED
    )
async def create_session(
        db: db_dependency,
        user: user_dependency,
        session_request: SessionRequest,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):

    subject = db.get(Subject, subject_id)
    if not subject or subject.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subject not found!')

    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Admin', 'Creator'])

    new_session = StudySession(
        title=session_request.title,
        description=session_request.description,
        date_time=session_request.date_time,
        duration=session_request.duration,
        status=session_request.status,
        subject_id=subject_id,
        created_by=user.user_id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        'success': 'Study Session successfully created.'
    }


@router.put(
    '/{group_id}/study_sessions/{subject_id}/{session_id}',
    status_code=status.HTTP_200_OK,
    response_model=SessionResponse
    )
async def update_session(
        db: db_dependency,
        user: user_dependency,
        session_update_request: SessionUpdateRequest,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0),
        session_id: int = Path(gt=0)
    ):

    subject = db.get(Subject, subject_id)
    if not subject or subject.group_id != group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subject not found!')

    member = get_group_member(db, user, group_id)
    require_role(member.role, ['Admin', 'Creator'])

    session = db.query(StudySession).filter(
        StudySession.subject_id == subject_id,
        StudySession.id == session_id
        ).first()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Study Session not found!')

    for field, value in session_update_request.model_dump(exclude_unset=True).items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)