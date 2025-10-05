from app.core.utils import validate_subject, validate_group, validate_role, validate_membership, validate_session
from app.schemas.study_session import SessionResponse, SessionRequest
from fastapi import APIRouter, HTTPException, Path
from app.dependencies import user_dependency
from app.core.constants import ALLOWED_ROLES
from app.models import StudySession
from starlette import status
from typing import List
from sqlalchemy.orm import joinedload
from app.database import db_dependency



router = APIRouter(
    prefix='/study-sessions',
    tags=['Study Sessions']
)


@router.get('/{group_id}/{subject_id}', status_code=status.HTTP_200_OK, response_model=List[SessionResponse])
def get_sessions_by_subject(
        db: db_dependency,
        user: user_dependency,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):
    """
    Retrieve all study sessions for a specific subject within a study group.
    Only members can perform this action.
    """
    validate_group(db, group_id)
    validate_membership(db, user.id, group_id)
    validate_subject(db, subject_id, group_id)

    sessions = db.query(StudySession).filter(StudySession.subject_id == subject_id).all()

    return sessions


@router.post('/{group_id}/{subject_id}', status_code=status.HTTP_201_CREATED, response_model=SessionResponse)
def create_session(
        db: db_dependency,
        user: user_dependency,
        session_request: SessionRequest,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):
    """
    Create a new study session under a specific subject and study group.
    Only Creator or Admin can perform this action.
    """
    validate_group(db, group_id)
    validate_subject(db, subject_id, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)


    new_session = StudySession(
        **session_request.model_dump(),
        subject_id=subject_id,
        created_by=user.id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.put('/{session_id}', status_code=status.HTTP_200_OK, response_model=SessionResponse)
def update_session(
        db: db_dependency,
        user: user_dependency,
        session_request: SessionRequest,
        session_id: int = Path(gt=0)
    ):
    """
    Update a study session's details if the authenticated user is the creator.
    Only fields provided in the request will be updated.
    """
    target_session = validate_session(db, session_id)
    if target_session.created_by != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action'
        )

    for field, value in session_request.model_dump(exclude_unset=True).items():
        setattr(target_session, field, value)

    db.commit()
    return target_session