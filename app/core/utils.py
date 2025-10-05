from app.models import StudyGroup, Membership, User, Subject, StudySession
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_, func
from starlette import status
from typing import Optional
from pydantic import EmailStr



def validate_role(member_role: str, allowed_roles: list[str]) -> None:
    """
    Ensure the member's role is authorized for the action.
    """
    if member_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to perform this action'
        )


def validate_membership(db: Session, user_id: int, group_id: int) -> Membership:
    """
    Verify that a user is a member of the given group.
    """
    member = db.query(Membership).filter(and_(
        Membership.user_id == user_id,
        Membership.group_id == group_id
    )).first()

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Membership required to access this group'
        )

    return member


def get_membership(db: Session, user_id: int, group_id: int) -> Membership | None:
    """
    Retrieve a membership record for a given user and group, if it exists.
    """
    member = db.query(Membership).filter(and_(
        Membership.user_id == user_id,
        Membership.group_id == group_id
    )).first()

    return member


def validate_group(db: Session, group_id: int) -> StudyGroup:
    """
    Retrieve a study group by ID, or raise 404 if not found.
    """
    group = db.get(StudyGroup, group_id)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified group could not be found'
        )

    return group


def validate_unique_group_name(db: Session, group_name: str, group_id: Optional[int] = None) -> None:
    """
    Ensure the group name is unique, excluding the given group ID if provided.
    """
    query = db.query(StudyGroup). filter(func.lower(StudyGroup.name) == group_name.lower())

    if group_id is not None:
        query = query.filter(StudyGroup.id != group_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Study group name is already in use'
        )


def validate_unique_email(db: Session, email: EmailStr) -> None:
    """
    Ensure that the given email address unique.
    Raise HTTP 400 Bad Request if the email is already in use.
    """
    query = db.query(User).filter(User.email == email).first()

    if query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email address is already in use'
        )


def validate_unique_username(db: Session, username: str) -> None:
    """
    Ensure that the given username unique.
    Raise HTTP 400 Bad Request if the username is already in use.
    """
    query = db.query(User).filter(User.username == username).first()

    if query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username is already in use'
        )


def validate_subject(db: Session, subject_id: int, group_id: int) -> Subject:
    """
    Retrieve a subject within a study group by ID, or raise 404 if not found.
    """
    subject = db.query(Subject).filter(and_(
        Subject.id == subject_id,
        Subject.group_id == group_id
    )).first()

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified subject could not be found'
        )

    return subject


def validate_unique_subject_name(db: Session, subject_name: str, group_id: int) -> None:
    """
    Ensure a subject name is unique within the specified study group.
    Raises an HTTP 409 error if a duplicate is found.
    """
    query = db.query(Subject).filter(and_(
        Subject.name == subject_name,
        Subject.group_id == group_id
        )).first()

    if query:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='A subject with this name is already in use'
        )


def validate_session(db: Session, session_id: int) -> StudySession:
    """
    Retrieve a session by ID, or raise 404 if not found.
    """
    session = db.get(StudySession, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='The specified study session could not be found'
        )

    return session