from app.schemas.subject import SubjectResponse, SubjectRequest
from app.schemas.common import MessageResponse
from app.dependencies import user_dependency
from app.core.constants import ALLOWED_ROLES
from app.database import db_dependency
from fastapi import APIRouter, Path
from app.models import Subject
from starlette import status
from typing import List
from app.core.utils import (
    validate_membership,
    validate_role,
    validate_group,
    validate_unique_subject_name,
    validate_subject
)



router = APIRouter(
    prefix='/subjects',
    tags=['Subjects']
)


@router.get('/{group_id}', status_code=status.HTTP_200_OK, response_model=List[SubjectResponse])
def get_subjects(db: db_dependency, user: user_dependency, group_id: int = Path(gt=0)):
    """
    Retrieve all subjects within a study group.
    Only members can perform this action.
    """
    validate_membership(db, user.id, group_id)
    subjects = db.query(Subject).filter(Subject.group_id == group_id).all()

    return subjects


@router.post('/{group_id}', status_code=status.HTTP_201_CREATED, response_model=SubjectResponse)
def create_subject(
        db: db_dependency,
        user: user_dependency,
        subject_request: SubjectRequest,
        group_id: int = Path(gt=0),
    ):
    """
    Create a new subject within a study group.
    Only Creator or Admin can perform this action.
    """
    validate_group(db, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)

    validate_unique_subject_name(db, subject_request.name, group_id)
    new_subject = Subject(**subject_request.model_dump(), group_id=group_id)

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return new_subject


@router.put('/{group_id}/{subject_id}', status_code=status.HTTP_200_OK, response_model=SubjectResponse)
def update_subject(
        db: db_dependency,
        user: user_dependency,
        subject_request: SubjectRequest,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):
    """
    Update the name of a subject in a study group.
    Only Creator or Admin can perform this action.
    """
    validate_group(db, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)

    target_subject = validate_subject(db, subject_id, group_id)
    validate_unique_subject_name(db, subject_request.name, group_id)

    target_subject.name = subject_request.name
    db.commit()

    return target_subject


@router.delete('/{group_id}/{subject_id}', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def delete_subject(
        db: db_dependency,
        user: user_dependency,
        group_id: int = Path(gt=0),
        subject_id: int = Path(gt=0)
    ):
    """
    Permanently delete a subject from a study group.
    Only Creator or Admin can perform this action.
    """
    validate_group(db, group_id)
    membership = validate_membership(db, user.id, group_id)
    validate_role(membership.role, ALLOWED_ROLES)

    target_subject = validate_subject(db, subject_id, group_id)

    db.delete(target_subject)
    db.commit()

    return MessageResponse(
        success=True,
        message='Subject deleted successfully'
    )
