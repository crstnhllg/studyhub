from app.core.security import validate_password, hash_password
from app.core.utils import validate_unique_email
from app.schemas.common import MessageResponse
from app.dependencies import user_dependency
from app.models import User, Membership
from app.database import db_dependency
from fastapi import APIRouter
from starlette import status
from typing import List
from app.schemas.user import (
    CurrentUserResponse,
    ChangeEmailRequest,
    ChangePassRequest,
    DeleteAccountRequest,
    UserMembershipResponse
)



router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=CurrentUserResponse)
def get_user_profile(user: user_dependency):
    """
    Retrieve the authenticated user's profile information.
    """
    return user


@router.get('/me/memberships', status_code=status.HTTP_200_OK, response_model=List[UserMembershipResponse])
def get_user_memberships(db: db_dependency, user: user_dependency):
    """
    Retrieve the list of groups the authenticated user belongs to with their roles.
    """
    memberships = db.query(Membership).filter(Membership.user_id == user.id).all()

    return memberships


@router.put('/email', status_code=status.HTTP_200_OK, response_model=CurrentUserResponse)
def update_user_email(db: db_dependency, user: user_dependency, email_request: ChangeEmailRequest):
    """
    Update the authenticated user's email address after verifying their password.
    """
    current_user = db.get(User, user.id)
    validate_password(email_request.password, current_user.hashed_password)
    validate_unique_email(db, email_request.new_email)

    current_user.email = email_request.new_email
    db.commit()

    return current_user


@router.put('/password', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def update_user_password(db: db_dependency, user: user_dependency, password_request: ChangePassRequest):
    """
    Update the authenticated user's password after verifying the current password.
    """
    current_user = db.get(User, user.id)
    validate_password(password_request.old_password, current_user.hashed_password)
    current_user.hashed_password = hash_password(password_request.new_password)

    db.commit()

    return MessageResponse(
        success=True,
        message='Password updated successfully'
    )


@router.delete('/me', status_code=status.HTTP_200_OK, response_model=MessageResponse)
def delete_account(db: db_dependency, user: user_dependency, delete_acc_request: DeleteAccountRequest):
    """
    Permanently delete the authenticated user's account after password confirmation.
    """
    current_user = db.get(User, user.id)
    validate_password(delete_acc_request.password, current_user.hashed_password)

    db.delete(current_user)
    db.commit()

    return MessageResponse(
        success=True,
        message='Account deleted successfully'
    )