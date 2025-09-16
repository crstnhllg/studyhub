from schemas.user import (
    CurrentUserResponse,
    ChangeEmailRequest,
    ChangePassRequest,
    DeleteAccountRequest,
    MembershipResponse,
    MessageResponse
)
from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user, bcrypt_context
from models import User, Membership
from starlette import status
from typing import Annotated, List
from database import get_db
from sqlalchemy.orm import Session, joinedload


router = APIRouter(
    prefix='/user',
    tags=['User']
)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[CurrentUserResponse, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK, response_model=CurrentUserResponse)
async def get_user_profile(user: user_dependency):
    return user


@router.get('/memberships', status_code=status.HTTP_200_OK, response_model=List[MembershipResponse])
async def get_memberships(db: db_dependency, user: user_dependency):
    memberships = db.query(Membership).options(
        joinedload(Membership.group)
    ).filter(Membership.user_id == user.user_id).all()

    return [
        MembershipResponse(
            group_id=m.group_id,
            group_name=m.group.name,
            role=m.role
        )
        for m in memberships
    ]


@router.put('/email', status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def update_email(db: db_dependency, user: user_dependency, email_request: ChangeEmailRequest):

    db_user = db.get(User, user.user_id)

    if not bcrypt_context.verify(email_request.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password!')

    email_exists = db.query(User).filter(User.email == email_request.new_email).first()
    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists!')

    db_user.email = email_request.new_email
    db.commit()
    return MessageResponse(
        success=True,
        message=f'Email successfully updated to {db_user.email}'
    )


@router.put('/password', status_code=status.HTTP_200_OK, response_model=MessageResponse)
async def update_password(db: db_dependency, user: user_dependency, password_request: ChangePassRequest):

    db_user = db.get(User, user.user_id)

    if not bcrypt_context.verify(password_request.old_password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password!')

    db_user.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.commit()
    return MessageResponse(
        success=True,
        message='Password successfully updated.'
    )


@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(db: db_dependency, user: user_dependency, delete_acc_request: DeleteAccountRequest) -> None:

    db_user = db.get(User, user.user_id)

    if not bcrypt_context.verify(delete_acc_request.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password!')

    db.delete(db_user)
    db.commit()